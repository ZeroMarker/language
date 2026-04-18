mdBook 本身不提供自动生成 `SUMMARY.md` 的命令，需要借助第三方工具或脚本实现。以下是几种主流方案。

---

## 1. 官方机制：`mdbook init`（仅生成初始框架）

`mdbook init` 命令会创建项目的基础结构和初始的 `SUMMARY.md`，包含 `intro.md` 和 `first.md` 两个默认章节。

但这只是一个一次性生成的初始框架，后续新增 Markdown 文件时不会自动更新 `SUMMARY.md`，因此不适合文档频繁增减的场景。

---

## 2. Rust 工具（推荐）

### 2.1 mdbook-auto-gen-summary

**安装**：
```bash
cargo install mdbook-auto-gen-summary
```

**两种使用方式**：

1. **命令行独立使用**：一次性生成 `SUMMARY.md`。
   ```bash
   mdbook-auto-gen-summary gen /path/to/your/mdbook/src
   ```
   添加 `-t` 参数可将 Markdown 文件的首行（而非文件名）作为链接文本。
   ```bash
   mdbook-auto-gen-summary gen -t /path/to/your/mdbook/src
   ```

2. **作为 mdBook 预处理器**：每次运行 `mdbook build` 或 `mdbook serve` 时自动生成。

在 `book.toml` 中配置：
```toml
[build]
create-missing = false

[preprocessor.auto-gen-summary]
first-line-as-link-text = true   # 是否使用文件首行作为链接文本
```

该工具会遍历源目录下的所有 Markdown 文件，并生成对应的 `SUMMARY.md`。

### 2.2 mdbook-autosummary

**安装**：
```bash
cargo install mdbook-autosummary
```

**配置**（在 `book.toml` 中）：
```toml
[preprocessor.autosummary]
index-name = "index.md"      # 文件夹首页文件名，默认为 index.md
ignore-hidden = true          # 是否忽略以 . 或 _ 开头的文件

[build]
create-missing = false
```

**重要限制**：
- 每个需要被包含的文件夹**必须**包含一个 `index.md`（或自定义的首页文件），该文件会被链接到目录中；没有首页文件的文件夹会被忽略。
- 每个 Markdown 文件最好以 `# 标题` 开头，否则会回退使用文件名作为目录显示文本。
- 首次运行前需要存在一个 `SUMMARY.md` 文件（可以为空），否则 mdBook 会构建失败。
- 实现方式较为 Hacky，某些情况下可能导致预处理被多次调用。

### 2.3 mdbook-generate-summary

纯 CLI 工具，用于为 mdBook 仓库生成 `SUMMARY.md`，适合将 mdBook 用作知识库的场景。

```bash
cargo install mdbook-generate-summary
```

注意该工具有一些特殊约定，需要每个子目录下有 `README.md` 文件作为入口，适用范围较窄。

### 2.4 mdbook-summary-generate

根据文件系统路径自动生成 `SUMMARY.md`，支持目录排序（可按数字前缀排序）。目录名由 `{type_name}_{file_name}` 组成，排序字段为 `type_name` 和 `file_name`，均为字母序。

```bash
cargo install mdbook-summary-generate
```

---

## 3. Python 脚本

### 3.1 通用 Python 脚本

网上存在一个 Python 脚本，会递归扫描指定目录及其子目录中的所有 Markdown 文件，并生成与 mdBook 兼容的 `SUMMARY.md`。

**使用方法**：
1. 打开脚本，修改 `src_directory` 变量指向 Markdown 文件所在的目录。
2. 可选：将需要排除的目录添加到 `ignore_dirs` 列表中。
3. 运行 `python path/to/script.py`。

**特性**：
- 支持自然排序（`use_natural_sort=True`），使数字顺序符合人类直觉（如 "1" 在 "10" 之前）。
- 支持排除特定目录。

### 3.2 RFCs 项目中的示例脚本

Rust RFCs 项目中有一个 `generate-book.py` 脚本，展示了如何根据文件系统布局自动生成 `SUMMARY.md`。该脚本递归扫描 `text` 目录，为每个 `.md` 文件创建目录条目，并支持子目录嵌套。

核心逻辑如下：
```python
entries = [e for e in os.scandir(path) if e.name.endswith('.md')]
entries.sort(key=lambda e: e.name)      # 按文件名排序
for entry in entries:
    name = entry.name[:-3]              # 去除 .md 后缀
    link_path = entry.path[5:]          # 获取相对路径
    summary.write(f'{indent}- [{name}]({link_path})\n')
```

---

## 4. 其他工具

- **mdbook-toc**：自动为每个 Markdown 页面生成页内目录（Table of Contents），但这是页内目录，而非全书章节导航的 `SUMMARY.md`。
- **mdbook-tools**：一个灵活的命令行工具，用于组织文件和创建 mdBooks，可自动化生成结构化的摘要文件。

---

## 5. 方案对比与选择建议

| 方案 | 类型 | 使用方式 | 适合场景 |
|------|------|----------|----------|
| `mdbook-auto-gen-summary` | Rust 工具 | 命令行 / 预处理器 | 通用，推荐首选 |
| `mdbook-autosummary` | Rust 工具 | 预处理器 | 需要复杂文件夹结构，注意限制 |
| Python 脚本 | Python 脚本 | 命令行 | 无 Rust 环境，需高度定制 |
| `mdbook init` | 官方命令 | 一次性初始化 | 仅初始框架，不维护更新 |

### 推荐选择

- **日常 mdBook 项目**：使用 `mdbook-auto-gen-summary` 作为预处理器集成，每次构建自动更新目录。
- **无 Rust 环境**：使用 Python 脚本，可根据需求自行定制。
- **复杂文件夹结构**：可尝试 `mdbook-autosummary`，但需注意其限制（每个文件夹必须有 `index.md`）。

建议将 `SUMMARY.md` 添加到 `.gitignore`，避免自动生成的文件被提交到版本库中造成冲突。