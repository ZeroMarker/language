#!/usr/bin/env python3
"""
生成 mdBook 的 SUMMARY.md 文件
扫描 src 目录下的所有 Markdown 文件，根据目录结构生成层级索引
每个文件夹的入口文件为 README.md（或 index.md）
"""

import os
import re
from pathlib import Path

SRC_DIR = "src"
SUMMARY_FILE = os.path.join(SRC_DIR, "SUMMARY.md")
INDEX_NAMES = ["README.md", "index.md"]
EXCLUDE_PATTERNS = [r".*backup.*", r".*old.*", r".*temp.*", r".*new.*", r".*test.*"]
EXCLUDE_DIRS = [".git", ".github", ".claude", ".qwen", "node_modules", "__pycache__"]

def should_include_file(filename: str) -> bool:
    """检查文件是否应该被包含在目录中"""
    lower_name = filename.lower()
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, lower_name):
            return False
    return True

def should_include_dir(dirname: str) -> bool:
    """检查目录是否应该被扫描"""
    return dirname not in EXCLUDE_DIRS and not dirname.startswith(".")

def extract_title_from_md(filepath: str) -> str:
    """从 Markdown 文件中提取标题（第一个一级标题）"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read(2048)  # 只读取前 2048 个字符
            match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if match:
                return match.group(1).strip()
    except (UnicodeDecodeError, IOError):
        pass

    # 如果没有找到标题，使用文件名（不含扩展名）
    name = os.path.splitext(os.path.basename(filepath))[0]
    # 将下划线和连字符替换为空格
    name = re.sub(r"[_-]", " ", name)
    # 首字母大写
    return name.title()

def find_index_file(dirpath: str) -> str:
    """在目录中查找入口文件（README.md 或 index.md）"""
    for index_name in INDEX_NAMES:
        index_path = os.path.join(dirpath, index_name)
        if os.path.exists(index_path):
            return index_path
    return None

def collect_files_and_dirs(root_dir: str, current_depth: int = 0):
    """递归收集文件和目录信息"""
    entries = []

    for item in sorted(os.listdir(root_dir)):
        item_path = os.path.join(root_dir, item)
        rel_path = os.path.relpath(item_path, SRC_DIR)

        if os.path.isdir(item_path):
            if not should_include_dir(item):
                continue

            # 查找目录的入口文件
            index_file = find_index_file(item_path)
            if index_file:
                # 目录有入口文件，将其作为目录项
                title = extract_title_from_md(index_file)
                entry = {
                    "type": "dir",
                    "path": rel_path.replace("\\", "/"),
                    "title": title,
                    "children": collect_files_and_dirs(item_path, current_depth + 1)
                }
                entries.append(entry)
            else:
                # 目录没有入口文件，跳过（不显示在目录中）
                pass
        else:
            # 文件
            if not item.endswith(".md"):
                continue
            if item in INDEX_NAMES:
                continue  # 入口文件已经在目录项中处理
            if not should_include_file(item):
                continue
            if item.lower() == "summary.md":
                continue  # 排除生成的目录文件本身

            title = extract_title_from_md(item_path)
            entry = {
                "type": "file",
                "path": rel_path.replace("\\", "/"),
                "title": title
            }
            entries.append(entry)

    return entries

def generate_summary_content(entries, depth=0):
    """生成 SUMMARY.md 内容"""
    lines = []
    indent = "  " * depth

    for entry in entries:
        if entry["type"] == "dir":
            lines.append(f'{indent}* [{entry["title"]}]({entry["path"]}/README.md)')
            lines.extend(generate_summary_content(entry["children"], depth + 1))
        else:  # file
            lines.append(f'{indent}* [{entry["title"]}]({entry["path"]})')

    return lines

def main():
    print(f"扫描目录: {SRC_DIR}")

    if not os.path.exists(SRC_DIR):
        print(f"错误: 目录 {SRC_DIR} 不存在")
        return

    entries = collect_files_and_dirs(SRC_DIR)

    # 生成内容
    lines = ["# Summary", ""]

    # 添加根级索引文件（README.md 或 index.md）作为第一个条目
    root_index = find_index_file(SRC_DIR)
    if root_index:
        root_title = extract_title_from_md(root_index)
        root_rel_path = os.path.relpath(root_index, SRC_DIR).replace("\\", "/")
        lines.append(f"* [{root_title}]({root_rel_path})")
        lines.append("")  # 空行分隔

    lines.extend(generate_summary_content(entries))

    # 写入文件
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    total_entries = len(entries) + (1 if root_index else 0)
    print(f"已生成 {SUMMARY_FILE}")
    print(f"包含 {total_entries} 个条目")

if __name__ == "__main__":
    main()