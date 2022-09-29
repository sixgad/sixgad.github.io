# -*- coding:utf-8 -*-

# @Author:      zp
# @Time:        2022/9/28 15:00

import os
import markdown
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

                # 图片路径处理
                b_data = {
                    "tags": tags,
                    "date": date,
                    "title": title,
                    "content": html
                }
                detail_template.stream(blog=b_data).dump(f'{default_config["blog_dir"]}/{blog}/article.html', encoding='utf-8')
                print(f'deal_blogs {default_config["blog_dir"]}/{blog}/{article}')


if __name__ == "__main__":
    print('start generate')
    # step1 清空index_dir下的.html文件
    clear_index()
    # step2 读取blog_dir下所有blog、收集构建blog_list信息、由.md生成article.html
    deal_blogs()
