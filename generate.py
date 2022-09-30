# -*- coding:utf-8 -*-

# @Author:      zp
# @Time:        2022/9/28 15:00

import os
import math
from re import T
import markdown
from lxml import etree
from lxml import html as lxhtml
from jinja2 import Environment, FileSystemLoader

default_config = {
    # index页展示文章数
    "page_size": 10,
    # 模版文件夹
    "base_template": "./basetp",
    # 博客文件夹
    "blog_dir": "./blog",
    # 生成列表页文件夹
    "index_dir": "./index",
    # markdown插件配置,
    "md_ext": ['markdown.extensions.extra', 'markdown.extensions.codehilite', 'markdown.extensions.tables',
               'markdown.extensions.toc', "markdown.extensions.meta"],
    # 每构建是否重新生成历史所有的“文章.html”
    "clear_history": True
}

collect_list = []


def clear_index():
    for ht in os.listdir(default_config["index_dir"]):
        if ht.endswith(".html"):
            os.remove(f'{default_config["index_dir"]}/{ht}')
            print(f'clear {ht}')


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

        if default_config["clear_history"] and os.path.exists(f'{default_config["blog_dir"]}/{blog}/article.html'):
            os.remove(f'{default_config["blog_dir"]}/{blog}/article.html')
            print(f'clear {default_config["blog_dir"]}/{blog}/article.html')

        # 当article.html不存在时，启动md->html
        if not os.path.exists(f'{default_config["blog_dir"]}/{blog}/article.html') and flag:
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
                    # 图片路径处理
                    shtml = etree.HTML(html)
                    # img src不包含http说明为本地图片
                    if len(shtml.xpath('//img[not(contains(@src, "http"))]')):
                        for src in shtml.xpath('//img[not(contains(@src, "http"))]'):
                            old_src = src.xpath('./@src')[0]
                            new_src = f'{default_config["blog_dir"]}/{blog}/{old_src}'
                            src.attrib['src'] = new_src
                        html = lxhtml.tostring(
                            shtml, encoding='utf-8').decode('utf-8')

                    b_data = {
                        "tags": tags,
                        "date": date,
                        "title": title,
                        "content": html
                    }
                    detail_template.stream(blog=b_data).dump(
                        f'{default_config["blog_dir"]}/{blog}/article.html', encoding='utf-8')
                    print(
                        f'deal_blogs {default_config["blog_dir"]}/{blog}/{article}')
                    # 为列表页收集每篇博客文章
                    collect_list.append(
                        {
                            "tags": tags,
                            "date": date,
                            "title": title,
                            "href": f'{default_config["blog_dir"]}/{blog}/article.html'
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
                one = {
                    "num": pad,
                    "url": f'{default_config["index_dir"]}/index{pad}.html'
                }
                if pad == current_page:
                    one["current"] = True
                padding.append(one)
            return padding
        res = {
            "first":  f'{default_config["index_dir"]}/index1.html',
            "last": f'{default_config["index_dir"]}/index{len(index_list)}.html',
            "padding": make_fenye()               
        }

        index_template.stream(blogs=index_list[i], pagedata=res).dump(
            f'{default_config["index_dir"]}/index{current_page}.html', encoding='utf-8')
        print(f'deal_index {current_page}')
    

if __name__ == "__main__":
    print('start generate')
    # step1 清空index_dir下的.html文件
    clear_index()
    # step2 读取blog_dir下所有blog、收集构建blog_list信息、由.md生成article.html
    deal_blogs()
    # step3 生成index页
    deal_index()