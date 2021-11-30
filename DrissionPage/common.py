# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
@File    :   common.py
"""
from html import unescape
from pathlib import Path
from re import split as re_SPLIT, search, sub
from shutil import rmtree
from typing import Union
from zipfile import ZipFile


def str_to_loc(loc: str) -> tuple:
    """处理元素查找语句                                                                    \n
    查找方式：属性、tag name及属性、文本、xpath、css selector、id、class                      \n
    @表示属性，.表示class，#表示id，=表示精确匹配，:表示模糊匹配，无控制字符串时默认搜索该字符串    \n
    示例：                                                                                \n
        .ele_class                       - class等于ele_class的元素                        \n
        .:ele_class                      - class含有ele_class的元素                        \n
        #ele_id                          - id等于ele_id的元素                              \n
        #:ele_id                         - id含有ele_id的元素                              \n
        @class:ele_class                 - class含有ele_class的元素                        \n
        @class=ele_class                 - class等于ele_class的元素                        \n
        @class                           - 带class属性的元素                               \n
        tag:div                          - div元素                                        \n
        tag:div@class:ele_class          - class含有ele_class的div元素                     \n
        tag:div@class=ele_class          - class等于ele_class的div元素                     \n
        tag:div@text():search_text       - 文本含有search_text的div元素                     \n
        tag:div@text()=search_text       - 文本等于search_text的div元素                     \n
        text:search_text                 - 文本含有search_text的元素                        \n
        text=search_text                 - 文本等于search_text的元素                        \n
        xpath://div[@class="ele_class"]  - 用xpath查找                                     \n
        css:div.ele_class                - 用css selector查找                              \n
        xpath://div[@class="ele_class"]  - 等同于 x://div[@class="ele_class"]              \n
        css:div.ele_class                - 等同于 c:div.ele_class                          \n
        tag:div                          - 等同于 t:div                                    \n
        text:search_text                 - 等同于 tx:search_text                           \n
        text=search_text                 - 等同于 tx=search_text                           \n
    """
    loc_by = 'xpath'

    # .和#替换为class和id查找
    if loc.startswith('.'):
        if loc.startswith(('.=', '.:',)):
            loc = loc.replace('.', '@class', 1)
        else:
            loc = loc.replace('.', '@class=', 1)

    elif loc.startswith('#'):
        if loc.startswith(('#=', '#:',)):
            loc = loc.replace('#', '@id', 1)
        else:
            loc = loc.replace('#', '@id=', 1)

    elif loc.startswith(('t:', 't=')):
        loc = f'tag:{loc[2:]}'

    elif loc.startswith(('tx:', 'tx=')):
        loc = f'text{loc[2:]}'

    # 根据属性查找
    if loc.startswith('@'):
        r = re_SPLIT(r'([:=])', loc[1:], maxsplit=1)
        if len(r) == 3:
            mode = 'exact' if r[1] == '=' else 'fuzzy'
            loc_str = _make_xpath_str('*', f'@{r[0]}', r[2], mode)
        else:
            loc_str = f'//*[@{loc[1:]}]'

    # 根据tag name查找
    elif loc.startswith(('tag:', 'tag=')):
        if '@' not in loc[4:]:
            loc_str = f'//*[name()="{loc[4:]}"]'
        else:
            at_lst = loc[4:].split('@', maxsplit=1)
            r = re_SPLIT(r'([:=])', at_lst[1], maxsplit=1)
            if len(r) == 3:
                mode = 'exact' if r[1] == '=' else 'fuzzy'
                arg_str = 'text()' if r[0] in ('text()', 'tx()') else f'@{r[0]}'
                loc_str = _make_xpath_str(at_lst[0], arg_str, r[2], mode)
            else:
                loc_str = f'//*[name()="{at_lst[0]}" and @{r[0]}]'

    # 根据文本查找
    elif loc.startswith(('text:', 'text=')):
        if len(loc) > 5:
            mode = 'exact' if loc[4] == '=' else 'fuzzy'
            loc_str = _make_xpath_str('*', 'text()', loc[5:], mode)
        else:
            loc_str = '//*[not(text())]'

    # 用xpath查找
    elif loc.startswith(('xpath:', 'xpath=')):
        loc_str = loc[6:]
    elif loc.startswith(('x:', 'x=')):
        loc_str = loc[2:]

    # 用css selector查找
    elif loc.startswith(('css:', 'css=')):
        loc_by = 'css selector'
        loc_str = loc[4:]
    elif loc.startswith(('c:', 'c=')):
        loc_by = 'css selector'
        loc_str = loc[2:]

    # 根据文本模糊查找
    else:
        if loc:
            loc_str = _make_xpath_str('*', 'text()', loc, 'fuzzy')
        else:
            loc_str = '//*[not(text())]'

    return loc_by, loc_str


def _make_xpath_str(tag: str, arg: str, val: str, mode: str = 'fuzzy') -> str:
    """生成xpath语句                                          \n
    :param tag: 标签名
    :param arg: 属性名
    :param val: 属性值
    :param mode: 'exact' 或 'fuzzy'，对应精确或模糊查找
    :return: xpath字符串
    """
    tag_name = '' if tag == '*' else f'name()="{tag}" and '

    if mode == 'exact':
        return f'//*[{tag_name}{arg}={_make_search_str(val)}]'

    elif mode == 'fuzzy':
        if arg == 'text()':
            tag_name = '' if tag == '*' else f'{tag}/'
            return f'//{tag_name}text()[contains(., {_make_search_str(val)})]/..'
        else:
            return f"//*[{tag_name}contains({arg},{_make_search_str(val)})]"

    else:
        raise ValueError("mode参数只能是'exact'或'fuzzy'。")


def _make_search_str(search_str: str) -> str:
    """将"转义，不知何故不能直接用 \ 来转义 \n
    :param search_str: 查询字符串
    :return: 把"转义后的字符串
    """
    parts = search_str.split('"')
    parts_num = len(parts)
    search_str = 'concat('

    for key, i in enumerate(parts):
        search_str += f'"{i}"'
        search_str += ',' + '\'"\',' if key < parts_num - 1 else ''

    search_str += ',"")'

    return search_str


def format_html(text: str, trans: bool = True) -> str:
    """处理html编码字符             \n
    :param text: html文本
    :param trans: 是否转码
    :return: 格式化后的html文本
    """
    if not text:
        return text

    if trans:
        text = unescape(text)

    return text.replace('\xa0', ' ')


def translate_loc(loc: tuple) -> tuple:
    """把By类型的loc元组转换为css selector或xpath类型的  \n
    :param loc: By类型的loc元组
    :return: css selector或xpath类型的loc元组
    """
    if len(loc) != 2:
        raise ValueError('定位符长度必须为2。')

    loc_by = 'xpath'

    if loc[0] == 'xpath':
        loc_str = loc[1]

    elif loc[0] == 'css selector':
        loc_by = 'css selector'
        loc_str = loc[1]

    elif loc[0] == 'id':
        loc_str = f'//*[@id="{loc[1]}"]'

    elif loc[0] == 'class name':
        loc_str = f'//*[@class="{loc[1]}"]'

    elif loc[0] == 'link text':
        loc_str = f'//a[text()="{loc[1]}"]'

    elif loc[0] == 'name':
        loc_str = f'//*[@name="{loc[1]}"]'

    elif loc[0] == 'tag name':
        loc_str = f'//{loc[1]}'

    elif loc[0] == 'partial link text':
        loc_str = f'//a[contains(text(),"{loc[1]}")]'

    else:
        raise ValueError('无法识别的定位符。')

    return loc_by, loc_str


def clean_folder(folder_path: str, ignore: list = None) -> None:
    """清空一个文件夹，除了ignore里的文件和文件夹  \n
    :param folder_path: 要清空的文件夹路径
    :param ignore: 忽略列表
    :return: None
    """
    ignore = [] if not ignore else ignore
    p = Path(folder_path)

    for f in p.iterdir():
        if f.name not in ignore:
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                rmtree(f, True)


def unzip(zip_path: str, to_path: str) -> Union[list, None]:
    """解压下载的chromedriver.zip文件"""
    if not zip_path:
        return

    with ZipFile(zip_path, 'r') as f:
        return [f.extract(f.namelist()[0], path=to_path)]


def get_exe_path_from_port(port: Union[str, int]) -> Union[str, None]:
    """获取端口号第一条进程的可执行文件路径      \n
    :param port: 端口号
    :return: 可执行文件的绝对路径
    """
    from os import popen
    from time import perf_counter
    process = popen(f'netstat -ano |findstr {port}').read().split('\n')[0]
    t = perf_counter()

    while not process and perf_counter() - t < 10:
        process = popen(f'netstat -ano |findstr {port}').read().split('\n')[0]

    processid = process.split(' ')[-1]

    if not processid:
        return
    else:
        file_lst = popen(f'wmic process where processid={processid} get executablepath').read().split('\n')
        return file_lst[2].strip() if len(file_lst) > 2 else None


def get_usable_path(path: Union[str, Path]) -> Path:
    """检查文件或文件夹是否有重名，并返回可以使用的路径           \n
    :param path: 文件或文件夹路径
    :return: 可用的路径，Path对象
    """
    path = Path(path)
    parent = path.parent
    path = parent / make_valid_name(path.name)
    name = path.stem if path.is_file() else path.name
    ext = path.suffix if path.is_file() else ''

    first_time = True

    while path.exists():
        r = search(r'(.*)_(\d+)$', name)

        if not r or (r and first_time):
            src_name, num = name, '1'
        else:
            src_name, num = r.group(1), int(r.group(2)) + 1

        name = f'{src_name}_{num}'
        path = parent / f'{name}{ext}'
        first_time = None

    return path


def make_valid_name(full_name: str) -> str:
    """获取有效的文件名                  \n
    :param full_name: 文件名
    :return: 可用的文件名
    """
    # ----------------去除前后空格----------------
    full_name = full_name.strip()

    # ----------------使总长度不大于255个字符（一个汉字是2个字符）----------------
    r = search(r'(.*)(\.[^.]+$)', full_name)  # 拆分文件名和后缀名
    if r:
        name, ext = r.group(1), r.group(2)
        ext_long = len(ext)
    else:
        name, ext = full_name, ''
        ext_long = 0

    while get_long(name) > 255 - ext_long:
        name = name[:-1]

    full_name = f'{name}{ext}'

    # ----------------去除不允许存在的字符----------------
    return sub(r'[<>/\\|:*?\n]', '', full_name)


def get_long(txt) -> int:
    """返回字符串中字符个数（一个汉字是2个字符）          \n
    :param txt: 字符串
    :return: 字符个数
    """
    txt_len = len(txt)
    return int((len(txt.encode('utf-8')) - txt_len) / 2 + txt_len)
