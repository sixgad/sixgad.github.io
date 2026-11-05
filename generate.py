# -*- coding:utf-8 -*-

# @Author:      zp
# @Time:        2022/9/28 15:00

import os
import json
import markdown
from jinja2 import Environment, FileSystemLoader

default_config = {
    # index页展示文章数
    "page_size": 10,
    # 模版文件夹
    "base_template": "basetp",
    # 博客文件夹
    "blog_dir": "blog",
    # 小白图解(eli5)文件夹
    "eli5_dir": "eli5",
    # 生成列表页文件夹, 只能放最外层, 不能修改
    "index_dir": ".",
    # markdown插件配置,
    "md_ext": ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
               'markdown.extensions.toc', "markdown.extensions.meta"],
}

collect_list = []


def collect_toc_tokens(tokens):
    # 展平 toc 扩展的标题树, 仅保留 level 2-3 (h2/h3), 重排为 h2>h3 两级;
    # 过滤后条目不足 2 个返回空 (详情页不出目录)
    items = []

    def walk(toks):
        for t in toks:
            if t["level"] in (2, 3):
                items.append(t)
            walk(t["children"])

    walk(tokens)
    root = []
    last_h2 = None
    for t in items:
        node = {"name": t["name"], "id": t["id"], "children": []}
        if t["level"] == 2:
            root.append(node)
            last_h2 = node
        elif last_h2 is not None:
            last_h2["children"].append(node)
        else:
            # 未出现 h2 前就是 h3: 提为顶层, 避免同级 h3 被误挂为前一个 h3 的子级
            root.append(node)
    return root if len(items) >= 2 else []


def build_toc_html(nodes):
    if not nodes:
        return ""

    def render(nodelist):
        lis = []
        for n in nodelist:
            sub = render(n["children"]) if n["children"] else ""
            lis.append('<li><a href="#%s">%s</a>%s</li>' % (n["id"], n["name"], sub))
        return "<ul>%s</ul>" % "".join(lis)

    return render(nodes)


def clear_index():
    for ht in os.listdir(default_config["index_dir"]):
        if ht.endswith(".html") and ht.startswith("index"):
            os.remove(f'{default_config["index_dir"]}/{ht}')


def deal_blogs():
    env = Environment(loader=FileSystemLoader("basetp"))
    detail_template = env.get_template('ori_detail.html')
    # 获取blog_dir下每篇文章的文件夹
    blogs = os.listdir(default_config["blog_dir"])
    blogs.sort(key=lambda x: int(x.split("-")[0]))
    for blog in blogs:
        # 遍历文章文件夹，找到.md文件
        flag = False
        for article in os.listdir(f'{default_config["blog_dir"]}/{blog}'):
            if article.endswith(".md"):
                flag = True
                break

        if os.path.exists(f'{default_config["blog_dir"]}/{blog}/article.html'):
            os.remove(f'{default_config["blog_dir"]}/{blog}/article.html')

        if flag:
            # 读取.md
            with open(f'{default_config["blog_dir"]}/{blog}/{article}', 'r', encoding='utf-8') as f:
                mdobj = markdown.Markdown(extensions=default_config["md_ext"])
                html = mdobj.convert(f.read())
                tags = mdobj.Meta.get('tags')
                date = mdobj.Meta.get('date')[0]
                title = mdobj.Meta.get('title')[0]
                private = mdobj.Meta.get('private', ['False'])[0]
                # 私有博客不生成html展示(只能说相对私有...)
                if 'no' in private.lower() or 'false' in private.lower():
                    print("deal", blog)
                    # # 图片路径处理
                    # shtml = etree.HTML(html)
                    # # img src不包含http说明为本地图片
                    # if len(shtml.xpath('//img[not(contains(@src, "http"))]')):
                    #     for src in shtml.xpath('//img[not(contains(@src, "http"))]'):
                    #         old_src = src.xpath('./@src')[0]
                    #         # 因为img和html在同一目录下 不需要调整url
                    #         new_src = f'{default_config["blog_dir"]}/{blog}/{old_src}'
                    #         src.attrib['src'] = new_src
                    #         html = lxhtml.tostring(shtml, encoding='utf-8').decode('utf-8')

                    # 目录: toc 扩展已给标题加 id, 这里取 level 2-3 生成折叠面板数据
                    toc_html = build_toc_html(collect_toc_tokens(getattr(mdobj, "toc_tokens", [])))
                    b_data = {
                        "tags": tags,
                        "date": date,
                        "title": title,
                        "content": html,
                        "toc": toc_html
                    }
                    detail_template.stream(blog=b_data, nav_prefix="../..").dump(
                        f'{default_config["blog_dir"]}/{blog}/article.html', encoding='utf-8')
                    # 为列表页收集每篇博客文章
                    collect_list.append(
                        {
                            "tags": tags,
                            "date": date,
                            "title": title,
                            "href": f'../{default_config["blog_dir"]}/{blog}/article.html'
                        }
                    )
                else:
                    print("私密文章", blog)


def deal_index():
    env = Environment(loader=FileSystemLoader("basetp"))
    index_template = env.get_template('ori_index.html')

    def split_list_by_n(list_collection, n):
        for i in range(0, len(list_collection), n):
            yield list_collection[i: i + n]
    index_list = []
    # 列表页倒序展示文章
    for i in split_list_by_n(list(reversed(collect_list)), default_config["page_size"]):
        index_list.append(i)
    for i in range(len(index_list)):
        current_page = i + 1

        def make_fenye():
            # current_page居中,前后各展示2页,总共展示5页
            start = current_page - 2
            end = current_page + 2
            if start <= 0:
                start = 1
            if end >= len(index_list):
                end = len(index_list)
            padding = []
            for pad in range(start, end+1):
                pad_html = f'index{pad}.html'
                if pad == 1:
                    pad_html = "index.html"
                one = {
                    "num": pad,
                    "url": pad_html
                }
                if pad == current_page:
                    one["current"] = True
                padding.append(one)
            return padding
        res = {
            "first":  'index.html',
            "last": f'index{len(index_list)}.html' if len(index_list) > 1 else 'index.html',
            "padding": make_fenye()
        }
        index_html = f'index{current_page}.html'
        if current_page == 1:
            index_html = "index.html"

        index_template.stream(
            blogs=index_list[i],
            pagedata=res,
            nav_prefix=".",
            nav_active="home",
        ).dump(
            f'{default_config["index_dir"]}/{index_html}', encoding='utf-8')


def deal_search():
    env = Environment(loader=FileSystemLoader("basetp"))
    search_template = env.get_template('ori_list.html')
    tmp_collect_list = []
    if collect_list:
        for idx, article in enumerate(reversed(collect_list)):
            article["id"] = idx+1
            article["tags"] = " ".join(article["tags"])
            tmp_collect_list.append(article)
        search_template.stream(
            blogs=tmp_collect_list, nav_prefix=".", nav_active="list",
        ).dump(
            f'{default_config["index_dir"]}/index-list.html', encoding='utf-8')


def deal_acg():
    env = Environment(loader=FileSystemLoader("basetp"))
    acg_template = env.get_template('ori_acg.html')
    with open(f'{default_config["blog_dir"]}/0-demo/acg.json', 'r', encoding='utf-8') as f:
        acg_data = json.load(f)
    acg_template.stream(acg=acg_data, nav_prefix=".", nav_active="acg").dump(
        f'{default_config["index_dir"]}/index-acg.html', encoding='utf-8')


def deal_eli5():
    # 小白图解：eli5/ 下每篇一个 N-slug/ 文件夹(自包含 index.html + meta.json)
    # 目录缺失或无合法条目时生成空状态页, 与 acg.json 缺失即崩的行为不同: 栏目可增量生长
    env = Environment(loader=FileSystemLoader("basetp"))
    eli5_template = env.get_template('ori_eli5.html')
    eli5_dir = default_config["eli5_dir"]
    entries = []
    if os.path.isdir(eli5_dir):
        for name in os.listdir(eli5_dir):
            folder = f'{eli5_dir}/{name}'
            meta_path = f'{folder}/meta.json'
            # 坏条目(缺 meta.json / 序号非数字)跳过并提示, 不影响其余条目
            if not (os.path.isdir(folder) and os.path.isfile(meta_path)
                    and name.split("-")[0].isdigit()):
                print("eli5 坏条目, 跳过", name)
                continue
            # meta.json 存在但损坏(BOM/语法错/非对象)同样按坏条目跳过, utf-8-sig 兼容记事本 BOM
            try:
                with open(meta_path, 'r', encoding='utf-8-sig') as f:
                    meta = json.load(f)
                if not isinstance(meta, dict):
                    raise ValueError("meta 不是 JSON 对象")
            except (ValueError, UnicodeDecodeError) as e:
                print("eli5 坏条目, 跳过", name, "-", e)
                continue
            if str(meta.get('draft', False)).lower() in ('true', 'yes', '1'):
                print("eli5 草稿, 跳过", name)
                continue
            try:
                num = int(name.split("-")[0])
            except ValueError:
                print("eli5 坏条目, 跳过", name)
                continue
            entries.append({
                "id": num,
                "title": meta.get('title', name),
                "date": meta.get('date', ''),
                "desc": meta.get('desc', ''),
                "href": f'./{eli5_dir}/{name}/index.html'
            })
    # 按序号倒序展示, 与文章列表一致
    entries.sort(key=lambda x: x["id"], reverse=True)
    print("deal eli5, 共", len(entries), "篇")
    eli5_template.stream(eli5=entries, nav_prefix=".", nav_active="eli5").dump(
        f'{default_config["index_dir"]}/index-eli5.html', encoding='utf-8')


def deal_hub():
    env = Environment(loader=FileSystemLoader("basetp"))
    hub_template = env.get_template('ori_hub.html')
    hub_template.stream(nav_prefix=".", nav_active="hub").dump(
        f'{default_config["index_dir"]}/index-hub.html', encoding='utf-8')


if __name__ == "__main__":
    print('start generate')
    # step1 清空index_dir下的.html文件
    clear_index()
    # step2 读取blog_dir下所有blog、收集构建blog_list信息、由.md生成article.html
    deal_blogs()
    # step3 生成index页
    deal_index()
    # step4 生成索引页
    deal_search()
    print("success generate")
    # 其他-动漫、音乐、小说推荐
    deal_acg()
    # 小白图解(eli5)
    deal_eli5()
    # 站点导航聚合页
    deal_hub()
