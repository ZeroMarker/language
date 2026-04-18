# language

This repo is for language learning.

## 项目结构

本项目使用 [mdBook](https://github.com/rust-lang/mdBook) 构建在线文档，按语系/语族分类组织学习笔记：

- **afro** - 亚非语系（阿拉伯语、希伯来语）
- **aust** - 南岛语系（印尼语、他加禄语）
- **germ** - 日耳曼语族（英语、德语）
- **indo** - 印度-伊朗语族（希腊语、印地语）
- **meta** - 元数据/语音学（IPA、声调等）
- **nige** - 尼日尔-刚果语系（斯瓦希里语、祖鲁语）
- **roma** - 罗曼语族（法语、意大利语、拉丁语、葡萄牙语、西班牙语）
- **sino** - 汉藏语系（日语、韩语、越南语、粤语、繁体中文）
- **slav** - 斯拉夫语族（波兰语、俄语）
- **taik** - 壮侗语系（泰语）

## 使用 mdBook

### 安装依赖

```powershell
# 安装 mdBook
cargo install mdbook

# 安装自动生成 SUMMARY.md 的预处理器
cargo install mdbook-autosummary
```

### 构建和预览

```powershell
# 构建文档
mdbook build

# 启动本地服务器并自动打开浏览器
mdbook serve --open
```

### 自动生成目录

本项目使用 `mdbook-autosummary` 预处理器自动生成 `SUMMARY.md`。每次运行 `mdbook build` 或 `mdbook serve` 时，会自动扫描 `src/` 目录下的所有 Markdown 文件并更新目录。

**重要说明**：
- 每个需要被包含的文件夹**必须**包含一个 `README.md`（或其他指定的首页文件）
- 每个 Markdown 文件最好以 `# 标题` 开头，否则会回退使用文件名作为目录显示文本
- 首次运行前需要存在一个 `SUMMARY.md` 文件（可以为空），否则 mdBook 会构建失败

手动创建空的 SUMMARY.md：

```powershell
New-Item -Path "src\SUMMARY.md" -ItemType File
```

## 添加新笔记

1. 在对应的语系目录下创建文件夹，并在文件夹中创建 `README.md` 作为入口（如 `sino/jp/grammar/README.md`）
2. 确保文件以 `# 标题` 开头（这样自动生成目录时会使用首行作为链接文本）
3. 运行 `mdbook build` 或 `mdbook serve`，目录会自动更新

## 配置说明

配置文件在 `book.toml` 中：

```toml
[build]
create-missing = false

[preprocessor.autosummary]
index-name = "README.md"      # 文件夹首页文件名，默认为 index.md
ignore-hidden = true          # 是否忽略以 . 或 _ 开头的文件
```

## 部署到 GitHub Pages

本项目已配置 GitHub Actions 工作流，可自动构建并部署到 GitHub Pages。

### 启用 GitHub Pages

1. 在 GitHub 仓库设置中，转到 "Pages" 部分
2. 在 "Build and deployment" 中选择 "GitHub Actions"
3. 工作流将自动部署到 `gh-pages` 分支

### 自定义域名（可选）

如需使用自定义域名：

1. 在仓库设置 -> Pages 中添加自定义域名
2. 在 `book.toml` 中更新 `git-repository-url` 和 `edit-url-template`：

   ```toml
   [output.html]
   git-repository-url = "https://github.com/your-username/language"
   edit-url-template = "https://github.com/your-username/language/edit/main/{path}"
   ```
   将 `your-username` 替换为你的 GitHub 用户名

### 手动构建和预览

```powershell
# 生成 SUMMARY.md
python generate_summary.py

# 构建文档
mdbook build

# 本地预览
mdbook serve --open
```
