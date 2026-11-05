# AGENTS

## 概述

- 本仓库为「爬客」博客的 GitHub Pages 站点（`sixgad.github.io`），对外说明见 `README.md`。
- 内容以静态 HTML/CSS/JS 为主；本地用 Python 将各文章目录下的 Markdown 转为 `article.html`，并生成首页分页、文章索引、ACG 推荐页、小白图解栏目页与导航聚合页（`index-hub.html`）。
- **工程取向**：保持「纯静态 + 少量手写 CSS」与现有 Python 生成流程，不引入 Node/npm 构建链；全站导航与视觉增量集中在 `static/css/site-v2.css`，模板仍复用 `static/css/style.css`、`plugin.css` 等与旧版主题兼容的资源。

## 技术栈

- Python：用于站点生成脚本（具体次版本以本机环境为准）。
- 依赖由 [uv](https://docs.astral.sh/uv/) 管理：直接依赖见 `pyproject.toml`（`Jinja2==3.1.2`、`Markdown==3.4.1`），全部依赖及传递依赖的精确版本锁定在 `uv.lock`。
- 模板与生成：`Jinja2` 加载 `basetp/` 下 `ori_*.html` 与三个 `frag_*.html` 片段（`frag_nav` 顶栏、`frag_theme` 主题防白闪、`frag_motion` 动效总开关）；`Markdown` 使用 `extra`、`codehilite`、`tables`、`toc`、`meta` 等扩展（配置见 `generate.py` 中 `default_config["md_ext"]`）。
- 前端静态资源：`static/css/` 下 `site-v2.css` 为 v2 增量层（视觉 token、暗色主题、动效体系均在此按版本分段追加），`style.css`/`plugin.css`/`github.css`/`pygments.css` 为继承层；`static/js/` 下仅存零依赖原生脚本 `site.js`（主题切换、回顶、代码复制、入场编排、inspector 悬停等）。jQuery、Bootstrap JS、`scripts.js`、远程 Poppins 字体已于 v2 改造移除；`plugin.css` 为清理过的 Bootstrap+图标字体子集（见项目陷阱）。无 `package.json`。`static/fonts/` 当前仅保留 Font Awesome 与 Simple Line Icons 的 **woff2** 文件（与 `plugin.css` 中 `@font-face` 一致）。
- 托管：`CNAME`（自定义域）、`.nojekyll`（禁用 Jekyll 处理）。

## 目录结构

- `blog/`：文章目录，子文件夹名为 `序号-标题`；内含源稿 `.md`（及图片等）、生成结果 `article.html`。
- `blog/0-demo/` 是例外而非文章：其中 `acg.json` 被 `generate.py` 的 `deal_acg()` 按固定路径读取，缺失会导致 `index-acg.html` 生成失败，勿当文章目录删改。
- `eli5/`：「小白图解」栏目内容目录，条目由 eli5-to-blog 技能（用户级，位于 `~/.agents/skills/eli5-to-blog/`，仓库外）经用户确认后写入。每篇一个 `序号-slug/` 子文件夹，内含讲解页 `index.html`（按生成原样落盘，不依赖站点资源）与 `meta.json`（`title`/`date`/`desc`，可选 `draft: true` 暂不收录）。序号独立于 blog 文章编号。`deal_eli5()` 扫描该目录生成 `index-eli5.html`：目录缺失或为空时生成空状态页而不报错；坏条目（缺 `meta.json`、序号非数字、meta 损坏）跳过并在控制台提示。
- `basetp/`：Jinja2 源模板——`ori_index.html`（首页分页）、`ori_detail.html`（文章页）、`ori_list.html`（索引）、`ori_acg.html`（ACG）、`ori_eli5.html`（小白图解）、`ori_hub.html`（导航聚合）；片段 `frag_nav.html`（顶栏导航）、`frag_theme.html`（主题防白闪内联判定）、`frag_motion.html`（动效总开关与会话入场门内联判定），片段均被各页 `include`。
- `static/`：全站公共 CSS/JS/字体与图片（如 `static/css/`、`static/js/`、`static/fonts/`、`static/images/`）。
- 仓库根目录：`generate.py` 为生成入口；`index.html`、`index2.html`… 为列表分页输出；`index-list.html`、`index-acg.html`、`index-eli5.html`、`index-hub.html` 为单页输出（运行生成脚本后更新）。
- `nb/`（不入库，已 gitignore）：`nb/specs/` 存 nb-spec-coding 各批功能 spec（含验收与 Rulings，是历次改造决策的权威过程记录，仅存在于本机）；`nb/adr/` 存达到门槛的架构决定。

## 编码规范

- 仓库内无 ESLint、Ruff、Black、EditorConfig 等统一工具链配置；修改时与现有 `generate.py`、模板与静态资源风格保持一致即可。
- 文章 Markdown 需带 `markdown.extensions.meta` 所需字段（脚本中读取 `tags`、`date`、`title`、`private` 等）；是否生成 `article.html` 由 `private` 的字符串判定（仅当取值（小写）中包含 `no` 或 `false` 时才生成，逻辑见 `generate.py`）。

## 常用命令

- 统一环境：venv 内含平台二进制与绝对路径，无法跨机器复用，故 `.venv/` 不入库（已加入 `.gitignore`）；每台机器在项目根运行 `uv sync`，uv 即按 `uv.lock` 在本地创建 `.venv` 并装齐锁定依赖。若机器上没有 `uv`，先 `pip install uv`（或使用官方独立安装脚本）。
- `uv run python generate.py`（运行前自动按 `uv.lock` 校验/补齐 `.venv`）：删除仓库根目录下所有以 `index` 开头且后缀为 `.html` 的文件后，扫描 `blog/` 中 Markdown，生成各篇 `article.html`，并重新生成分页首页、`index-list.html`、`index-acg.html`、`index-eli5.html` 与 `index-hub.html`。

## 禁止事项

- 勿向仓库提交密钥、令牌或本地 `.env`（`.gitignore` 已忽略 `.env` 与常见虚拟环境目录）。
- 勿绕过 `uv sync` 手动往 `.venv` 装包、或用系统 Python 运行 `generate.py`：依赖及其传递依赖的版本与 `uv.lock` 不一致（旧方案中未钉死的 Pygments 等即是教训），会让重新生成的 HTML 产生大量版本漂移 diff。
- 勿在文档中编造仓库未出现的依赖、脚本或 CI；技术栈与命令须能在 `pyproject.toml`、`uv.lock`、`generate.py` 等文件中得到印证。

- 勿手改生成物（根目录 `index*.html`、各篇 `blog/*/article.html`）：每次运行生成脚本会整体重写，改动必须经 `basetp/` 模板后重新生成。

## 导航

- 当需要了解 v2 系列改造（暗色/TOC/动效/CSS 清理等）某批的验收口径、取舍或 Rulings 时，读取 `nb/specs/` 内对应日期的 spec：该目录按批次保存完整决策过程，仅存在于本机。

## 项目陷阱

- `plugin.css` 已非常规 vendor 原文：按「65 生成页 + site.js 语料的保守 token 判据」移除死规则后以原文段拼接（提交 3c5645d）。升级或替换 Bootstrap/图标库不可直接覆盖，需在新文件上重跑同等清理。
- 首页「阅读全文」按钮是 `pointer-events:none` 的视觉件：真实点击目标是 stretched-link 覆盖的整卡，勿当 bug「修复」回独立可点（会产生双焦点停靠，违背 v2.3 验收）。
- `frag_theme.html` 与 `frag_motion.html` 两个 head 内联片段必须保留在各页 `<head>`、CSS 链接之后 body 之前：移动或删除会导致主题首帧闪烁、动效降级失效，以及入场重放经由跨文档 View Transition 空快照回归为页间白闪（提交 4aa511c）。
- 入场动画带会话门（sessionStorage `pk-intro`，每标签页仅首个文档播放）：测试时看不到入场动画先开新标签页验证，勿误判为失效。
- 暗色与动效全部样式声明以 html 上的 `data-theme` / `v2-motion`（+`v2-intro`）为作用域：主题或动效相关新样式须挂对应前缀，裸选择器书写会绕过降级。
