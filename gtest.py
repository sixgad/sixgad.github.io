import json,re
import shutil,math
import sys, random,os
from pathlib import Path

import markdown
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from gfm import AutolinkExtension


def __all_html_fiels_info(html_dir, page_size):
    """
    在dist根目录的直接置顶
    :param html_dir:
    :param page_size:
    :return:
    """
    info = {} # 0:[(url, title, pub_date, read_cnt)]

    temp_info = []
    top_fix = []  # 置顶文章
    html_list = list(Path(html_dir).glob('**/*.html'))

    for html in html_list:
        relative_path = html.relative_to(html_dir)
        pub_date = "-".join([str(x) for x in relative_path.parts[:-1]])
        if pub_date=='':
            top_fix.append((str(relative_path), relative_path.stem,  pub_date, random.randint(100, 9999)))
        else:
            temp_info.append((str(relative_path), relative_path.stem,  pub_date, random.randint(100, 9999)))

    new_info = sorted(temp_info, key=lambda x: x[2],  reverse = True)
    post_len = len(new_info)
    page_cnt = math.ceil(post_len/page_size)
    for i in range(0, page_cnt):
        info[i] = new_info[i*page_size: min(i*page_size+page_size, post_len)]

    return info,top_fix


def __all_md_files(md_source_dir, dist_dir):
    md_2_html_path = {}
    md_list = list(Path(md_source_dir).glob('**/*.md'))
    md_list += list(Path(md_source_dir).glob('**/*.MD'))
    for md in md_list:
        html_file_name = f"{md.stem}.html"
        p = str(md.relative_to(md_source_dir).parent)
        p = re.sub("[\\\\/]", "-", p)
        html_path = Path(f"{dist_dir}/{p}/{html_file_name}")
        Path(html_path.parent).mkdir(parents=True, exist_ok=True)
        md_2_html_path[str(md)] = str(html_path)
    return md_2_html_path


def __process_image(mdpath, source_dir, dist_dir, html, html_file):
    soup = BeautifulSoup(html, "lxml")
    images = soup.find_all("img")
    for img in images:
        src = img.get("src")
        if src is not None and not src.startswith("http"):  # 说明是本地图片
            s = f"{Path(mdpath).parent}/{src}"
            d = f"{dist_dir}/{Path(html_file).relative_to(dist_dir).parent}/{src}"
            Path(Path(d).parent).mkdir(parents=True, exist_ok=True)
            shutil.copy(s, d)


def __copy_cname(source_dir, dist_dir):
    file = f"{source_dir}/CNAME"
    shutil.copy(file, dist_dir)


def __copy_resource(template_theme_dir, theme_static, dist_dir):
    for x in theme_static:
        source_dir = f"{template_theme_dir}/{x}"
        dist = f'{dist_dir}/{x}'
        shutil.copytree(source_dir, dist)


def __get_config(cfg_file="config.json"):
    """
    如果当前目录有就用，否则用自带的默认
    :param cfg_file:
    :return:
    """
    bin_dir = str(Path(__file__).parent)
    default_cfg = f"{bin_dir}/config.json"
    if os.path.exists(cfg_file):
        default_cfg = cfg_file

    if not os.path.exists(default_cfg):
        print(f"没找到config.json, 一般应将该位于你的博客最外层")
        exit(-1)

    with open(default_cfg, "r", encoding='utf-8') as f:
        txt = f.read()
    json_obj = json.loads(txt)

    return f"{bin_dir}/{json_obj['template_dir']}", json_obj['theme'], json_obj['theme_static'], json_obj['markdown_extensions'], json_obj['page_size'], json_obj['pagger_len']


def __tiny_png_b64(app_key):
    pass


def main(source_dir, dist_dir):
    shutil.rmtree(dist_dir, ignore_errors=True)
    template_dir, theme, theme_static, markdown_extentions, page_size, pagger_len = __get_config("config.json")
    template_theme_dir = f'{template_dir}/{theme}'
    env = Environment(loader=FileSystemLoader(template_theme_dir))
    detail_template = env.get_template('detail.html')
    index_template = env.get_template('index.html')

    md_2_html = __all_md_files(source_dir, dist_dir)
    tags_article = {}
    for md, html_file in md_2_html.items():
        Path(Path(html_file).parent).mkdir(parents=True, exist_ok=True)
        with open(md, 'r', encoding='utf-8') as f:
            markdown_extentions.append(AutolinkExtension())
            mdobj = markdown.Markdown(extensions=markdown_extentions)
            html = mdobj.convert(f.read())
            tags = mdobj.Meta.get('tags')
            table_of_content = mdobj.toc
            mdobj.toc=None
            if tags:
                for t in tags:
                    articles = tags_article.get(t)
                    if articles is None:
                        tags_article[t] = []
                    tags_article[t].append(Path(html_file).relative_to(dist_dir))

            __process_image(md, source_dir, dist_dir, html, html_file)
        static_path = "../"*(len(Path(html_file).relative_to(dist_dir).parents)-1)
        title = Path(html_file).stem
        detail_template.stream(post_content=html, static_path=static_path, title=title, tags=tags, toc=table_of_content).dump(html_file, encoding='utf-8')

    __copy_resource(template_theme_dir, theme_static, dist_dir)

    #####  接下来生成博客列表和分页
    pagegger_info, top_fix = __all_html_fiels_info(dist_dir, page_size)
    total_page = len(pagegger_info.keys())
    for idx, post_list in pagegger_info.items():
        if idx==0:
            list_page = f"{dist_dir}/index.html"
        else:
            list_page = f"{dist_dir}/index_{idx}.html"
        static_path = "../" * (len(Path(list_page).relative_to(dist_dir).parents) - 1)

        start_page = max(0, idx-pagger_len//2)
        end_page = min(total_page, idx+pagger_len//2)
        if idx-pagger_len//2<0:
            start_page =0
            end_page = min(total_page, 0+pagger_len)
        elif idx+pagger_len//2>total_page:
            start_page = max(0, total_page-pagger_len)
            end_page = total_page

        pagger_idx = range(start_page, end_page)
        index_template.stream(post=top_fix+post_list, static_path=static_path, pagegger = pagegger_info, pagger_idx=pagger_idx, cur_page = idx).dump(list_page, encoding='utf-8')
    __copy_cname(source_dir, dist_dir)

    tag_template = env.get_template("tag.html")
    Path(f"{dist_dir}/tags").mkdir(parents=True, exist_ok=True)
    for tag, article_list in tags_article.items():
        new_article_list = [(f'../{str(x)}', x.stem, str(x)[0:-len(x.name)]) for x in article_list] # url, title, pub_date
        tag_template.stream(post=new_article_list, static_path="../", title=f"分类_{tag}").dump(f"{dist_dir}/tags/tag_{tag}.html", encoding='utf-8')


if __name__=="__main__":
    cur_dir = Path(__file__).parent
    print(cur_dir)