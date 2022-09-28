# -*- coding:utf-8 -*-

# @Author:      zp
# @Time:        2022/9/28 15:00

from jinja2 import Environment, FileSystemLoader

if __name__ == "__main__":
    env = Environment(loader=FileSystemLoader("basetp"))
    index_template = env.get_template('index.html')
    index_template.stream(blog={"title": "jinja2 title", "doc": "jinja2 doc <a href='https://paker.net.cn' target='_blank'>jump</a>"}).dump("./index/index1.html", encoding='utf-8')