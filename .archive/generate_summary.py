#!/usr/bin/env python3
"""
生成 mdBook 的 SUMMARY.md 文件
扫描 src 目录下的所有 Markdown 文件，根据目录结构生成层级索引
每个文件夹的入口文件为 README.md（或 index.md）
"""

import re
from pathlib import Path

SRC_DIR = Path("src")
SUMMARY_FILE = SRC_DIR / "SUMMARY.md"
INDEX_NAMES = ("README.md", "index.md")
EXCLUDE_PATTERNS = (
    r"(^|[._-])(backup|old|temp|tmp|draft|bak)([._-]|$)",
    r"~$",
    r"\.bak$",
    r"\.tmp$",
    r"\.sw[po]$",
)
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


def clean_markdown_title(title: str) -> str:
    """清理 Markdown 标题文本。"""
    title = title.strip().strip("#").strip()
    title = re.sub(r"`([^`]+)`", r"\1", title)
    title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
    return title


def extract_title_from_md(filepath: Path) -> str:
    """从 Markdown 文件中提取标题（第一个一级标题）"""
    try:
        with filepath.open("r", encoding="utf-8") as f:
            content = f.read(2048)  # 只读取前 2048 个字符
            match = re.search(r"^#\s+(.+?)\s*$", content, re.MULTILINE)
            if match:
                return clean_markdown_title(match.group(1))
    except (UnicodeDecodeError, IOError):
        pass

    # 如果没有找到标题，使用文件名（不含扩展名）
    name = filepath.stem
    # 将下划线和连字符替换为空格
    name = re.sub(r"[_-]", " ", name)
    # 首字母大写
    return name.title()


def find_index_file(dirpath: Path) -> Path | None:
    """在目录中查找入口文件（README.md 或 index.md）"""
    files_by_lower_name = {path.name.lower(): path for path in dirpath.iterdir() if path.is_file()}
    for index_name in INDEX_NAMES:
        index_path = files_by_lower_name.get(index_name.lower())
        if index_path:
            return index_path
    return None


def to_summary_path(path: Path) -> str:
    """转换为 SUMMARY.md 中使用的相对路径。"""
    return path.relative_to(SRC_DIR).as_posix()


def sort_key(path: Path):
    """目录优先，然后按名称自然排序。"""
    parts = re.split(r"(\d+)", path.name.lower())
    natural_name = [int(part) if part.isdigit() else part for part in parts]
    return (not path.is_dir(), natural_name)


def collect_files_and_dirs(root_dir: Path):
    """递归收集文件和目录信息"""
    entries = []

    for item_path in sorted(root_dir.iterdir(), key=sort_key):
        item = item_path.name
        if item_path.is_dir():
            if not should_include_dir(item):
                continue

            # 查找目录的入口文件
            index_file = find_index_file(item_path)
            if index_file:
                # 目录有入口文件，将其作为目录项
                title = extract_title_from_md(index_file)
                entry = {
                    "type": "dir",
                    "path": to_summary_path(index_file),
                    "title": title,
                    "children": collect_files_and_dirs(item_path)
                }
                entries.append(entry)
        else:
            # 文件
            if item_path.suffix.lower() != ".md":
                continue
            if item.lower() in {name.lower() for name in INDEX_NAMES}:
                continue  # 入口文件已经在目录项中处理
            if not should_include_file(item):
                continue
            if item.lower() == "summary.md":
                continue  # 排除生成的目录文件本身

            title = extract_title_from_md(item_path)
            entry = {
                "type": "file",
                "path": to_summary_path(item_path),
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
            lines.append(f'{indent}* [{entry["title"]}]({entry["path"]})')
            lines.extend(generate_summary_content(entry["children"], depth + 1))
        else:  # file
            lines.append(f'{indent}* [{entry["title"]}]({entry["path"]})')

    return lines


def count_entries(entries):
    """递归统计条目数量。"""
    total = 0
    for entry in entries:
        total += 1
        if entry["type"] == "dir":
            total += count_entries(entry["children"])
    return total


def main():
    print(f"扫描目录: {SRC_DIR}")

    if not SRC_DIR.exists():
        print(f"错误: 目录 {SRC_DIR} 不存在")
        return

    entries = collect_files_and_dirs(SRC_DIR)

    # 生成内容
    lines = ["# Summary", ""]

    # 添加根级索引文件（README.md 或 index.md）作为第一个条目
    root_index = find_index_file(SRC_DIR)
    if root_index:
        root_title = extract_title_from_md(root_index)
        root_rel_path = to_summary_path(root_index)
        lines.append(f"* [{root_title}]({root_rel_path})")
        lines.append("")  # 空行分隔

    lines.extend(generate_summary_content(entries))
    content = "\n".join(lines) + "\n"

    # 写入文件
    if SUMMARY_FILE.exists() and SUMMARY_FILE.read_text(encoding="utf-8") == content:
        print(f"{SUMMARY_FILE} 无变化")
    else:
        SUMMARY_FILE.write_text(content, encoding="utf-8")
        print(f"已生成 {SUMMARY_FILE}")

    total_entries = count_entries(entries) + (1 if root_index else 0)
    print(f"包含 {total_entries} 个条目")


if __name__ == "__main__":
    main()
