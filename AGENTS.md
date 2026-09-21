# AGENTS

## 概述

- 本仓库为「爬客」博客的 GitHub Pages 站点（`sixgad.github.io`），对外说明见 `README.md`。
- 内容以静态 HTML/CSS/JS 为主；本地用 Python 将各文章目录下的 Markdown 转为 `article.html`，并生成首页分页、文章索引、ACG 推荐页与导航聚合页（`index-hub.html`）。
- **工程取向**：保持「纯静态 + 少量手写 CSS」与现有 Python 生成流程，不引入 Node/npm 构建链；全站导航与视觉增量集中在 `static/css/site-v2.css`，模板仍复用 `static/css/style.css`、`plugin.css` 等与旧版主题兼容的资源。

## 技术栈

- Python：用于站点生成脚本（具体次版本以本机环境为准）。
- 依赖由 [uv](https://docs.astral.sh/uv/) 管理：直接依赖见 `pyproject.toml`（`Jinja2==3.1.2`、`Markdown==3.4.1`），全部依赖及传递依赖的精确版本锁定在 `uv.lock`。
- 模板与生成：`Jinja2` 加载 `basetp/` 下 `ori_*.html` 与 `frag_nav.html`；`Markdown` 使用 `extra`、`codehilite`、`tables`、`toc`、`meta` 等扩展（配置见 `generate.py` 中 `default_config["md_ext"]`）。
- 前端静态资源：`static/` 下 Bootstrap、jQuery、合并版 `plugin.js`/`plugin.css`（内含 Bootstrap 与图标字体样式）、`site-v2.css` 等；无 `package.json`。`static/fonts/` 当前仅保留 Font Awesome 与 Simple Line Icons 的 **woff2** 文件（与 `plugin.css` 中 `@font-face` 一致）。
- 托管：`CNAME`（自定义域）、`.nojekyll`（禁用 Jekyll 处理）。

## 目录结构

- `blog/`：文章目录，子文件夹名为 `序号-标题`；内含源稿 `.md`（及图片等）、生成结果 `article.html`。
- `blog/0-demo/` 是例外而非文章：其中 `acg.json` 被 `generate.py` 的 `deal_acg()` 按固定路径读取，缺失会导致 `index-acg.html` 生成失败，勿当文章目录删改。
- `basetp/`：Jinja2 源模板——`ori_index.html`（首页分页）、`ori_detail.html`（文章页）、`ori_list.html`（索引）、`ori_acg.html`（ACG）、`ori_hub.html`（导航聚合）、`frag_nav.html`（顶栏导航片段，被各页 `include`）。
- `static/`：全站公共 CSS/JS/字体与图片（如 `static/css/`、`static/js/`、`static/fonts/`、`static/images/`）。
- 仓库根目录：`generate.py` 为生成入口；`index.html`、`index2.html`… 为列表分页输出；`index-list.html`、`index-acg.html`、`index-hub.html` 为单页输出（运行生成脚本后更新）。

## 编码规范

- 仓库内无 ESLint、Ruff、Black、EditorConfig 等统一工具链配置；修改时与现有 `generate.py`、模板与静态资源风格保持一致即可。
- 文章 Markdown 需带 `markdown.extensions.meta` 所需字段（脚本中读取 `tags`、`date`、`title`、`private` 等）；是否生成 `article.html` 由 `private` 的字符串判定（仅当取值（小写）中包含 `no` 或 `false` 时才生成，逻辑见 `generate.py`）。

## 常用命令

- 统一环境：venv 内含平台二进制与绝对路径，无法跨机器复用，故 `.venv/` 不入库（已加入 `.gitignore`）；每台机器在项目根运行 `uv sync`，uv 即按 `uv.lock` 在本地创建 `.venv` 并装齐锁定依赖。若机器上没有 `uv`，先 `pip install uv`（或使用官方独立安装脚本）。
- `uv run python generate.py`（运行前自动按 `uv.lock` 校验/补齐 `.venv`）：删除仓库根目录下所有以 `index` 开头且后缀为 `.html` 的文件后，扫描 `blog/` 中 Markdown，生成各篇 `article.html`，并重新生成分页首页、`index-list.html`、`index-acg.html` 与 `index-hub.html`。

## 禁止事项

- 勿向仓库提交密钥、令牌或本地 `.env`（`.gitignore` 已忽略 `.env` 与常见虚拟环境目录）。
- 勿绕过 `uv sync` 手动往 `.venv` 装包、或用系统 Python 运行 `generate.py`：依赖及其传递依赖的版本与 `uv.lock` 不一致（旧方案中未钉死的 Pygments 等即是教训），会让重新生成的 HTML 产生大量版本漂移 diff。
- 勿在文档中编造仓库未出现的依赖、脚本或 CI；技术栈与命令须能在 `pyproject.toml`、`uv.lock`、`generate.py` 等文件中得到印证。
