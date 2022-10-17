# -*- coding:utf-8 -*-

# @Author:      zp
# @Time:        2022/9/28 15:00

import os
import json
import random
import markdown
# from lxml import etree
# from lxml import html as lxhtml
from jinja2 import Environment, FileSystemLoader

default_config = {
    # index页展示文章数
    "page_size": 10,
    # 模版文件夹
    "base_template": "basetp",
    # 博客文件夹
    "blog_dir": "blog",
    # 生成列表页文件夹, 只能放最外层, 不能修改
    "index_dir": ".",
    # markdown插件配置,
    "md_ext": ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
               'markdown.extensions.toc', "markdown.extensions.meta"],
}

collect_list = []


def clear_index():
    for ht in os.listdir(default_config["index_dir"]):
        if ht.endswith(".html") and ht.startswith("index"):
            os.remove(f'{default_config["index_dir"]}/{ht}')


def deal_blogs():
    env = Environment(loader=FileSystemLoader("basetp"))
    detail_template = env.get_template('ori_detail.html')
    # 获取blog_dir下每篇文章的文件夹
    blogs = os.listdir(default_config["blog_dir"])
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
                print("deal", blog)
                mdobj = markdown.Markdown(extensions=default_config["md_ext"])
                html = mdobj.convert(f.read())
                tags = mdobj.Meta.get('tags')
                date = mdobj.Meta.get('date')[0]
                title = mdobj.Meta.get('title')[0]
                private = mdobj.Meta.get('private', ['False'])[0]
                # 私有博客不生成html展示(只能说相对私有...)
                if 'no' in private.lower() or 'false' in private.lower():
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

                    b_data = {
                        "tags": tags,
                        "date": date,
                        "title": title,
                        "content": html
                    }
                    detail_template.stream(blog=b_data).dump(
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


def deal_index():
    env = Environment(loader=FileSystemLoader("basetp"))
    index_template = env.get_template('ori_index.html')

    def split_list_by_n(list_collection, n):
        for i in range(0, len(list_collection), n):
            yield list_collection[i: i + n]
    index_list = []
    for i in split_list_by_n(collect_list, default_config["page_size"]):
        index_list.append(i)
    for i in range(len(index_list)):
        current_page = i + 1

        def make_fenye():
            # current_page居中,前后各展示2页,总共展示5页
            start = current_page - 2
            end = current_page + 2
            if start < 0:
                start = 1
            if end > len(index_list):
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

        index_template.stream(blogs=index_list[i], pagedata=res).dump(
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
        search_template.stream(blogs=tmp_collect_list).dump(
            f'{default_config["index_dir"]}/index-list.html', encoding='utf-8')


def deal_acg():
    env = Environment(loader=FileSystemLoader("basetp"))
    acg_template = env.get_template('ori_acg.html')
    with open(f'{default_config["blog_dir"]}/0demo/acg.json', 'r', encoding='utf-8') as f:
        acg_data = json.load(f)
    corlors = ["table-active", "table-success",
               "table-warning", "table-danger"]
    for i in acg_data:
        i["corlor"] = corlors[random.randint(0, 3)]
    acg_template.stream(acg=acg_data).dump(
        f'{default_config["index_dir"]}/index-acg.html', encoding='utf-8')


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
