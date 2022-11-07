# -*- coding:utf-8 -*-
from typing import Union, Tuple, List

from DownloadKit import DownloadKit
from pychrome import Tab
from requests import Session, Response
from requests.structures import CaseInsensitiveDict
from tldextract import extract

from .chrome_element import ChromeElement
from .session_element import SessionElement
from .base import BasePage
from .config import DriverOptions, SessionOptions, _cookies_to_tuple
from .chrome_page import ChromePage
from .session_page import SessionPage


class WebPage(SessionPage, ChromePage, BasePage):
    def __init__(self,
                 mode: str = 'd',
                 timeout: float = 10,
                 tab_handle: str = None,
                 driver_or_options: Union[Tab, DriverOptions, bool] = None,
                 session_or_options: Union[SessionOptions, SessionOptions, bool] = None) -> None:
        """初始化函数                                                                                            \n
        :param mode: 'd' 或 's'，即driver模式和session模式
        :param timeout: 超时时间，d模式时为寻找元素时间，s模式时为连接时间，默认10秒
        :param driver_or_options: Tab对象或浏览器设置，只使用s模式时应传入False
        :param session_or_options: Session对象或requests设置，只使用d模式时应传入False
        """
        self._mode = mode.lower()
        if self._mode not in ('s', 'd'):
            raise ValueError('mode参数只能是s或d。')

        super(ChromePage, self).__init__(timeout)  # 调用Base的__init__()
        self._session = None
        self._driver = None
        self._set_session_options(session_or_options)
        self._set_driver_options(driver_or_options)
        self._setting_handle = tab_handle
        self._has_driver, self._has_session = (None, True) if self._mode == 's' else (True, None)
        self._response = None

        if self._mode == 'd':
            self._ready()

        # if self._mode == 'd':
        #     try:
        #         timeouts = self.drission.driver_options.timeouts
        #         t = timeout if timeout is not None else timeouts['implicit'] / 1000
        #         self.set_timeouts(t, timeouts['pageLoad'] / 1000, timeouts['script'] / 1000)
        #
        #     except Exception:
        #         self.timeout = timeout if timeout is not None else 10

    def __call__(self,
                 loc_or_str: Union[Tuple[str, str], str, ChromeElement, SessionElement],
                 timeout: float = None) -> Union[ChromeElement, SessionElement, str, None]:
        """在内部查找元素                                            \n
        例：ele = page('@id=ele_id')                               \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 超时时间
        :return: 子元素对象或属性文本
        """
        if self._mode == 's':
            return super().__call__(loc_or_str)
        elif self._mode == 'd':
            return super(SessionPage, self).__call__(loc_or_str, timeout)

    # -----------------共有属性和方法-------------------
    @property
    def url(self) -> Union[str, None]:
        """返回当前url"""
        if self._mode == 'd':
            return super(SessionPage, self).url if self._has_driver else None
        elif self._mode == 's':
            return self._session_url

    @property
    def html(self) -> str:
        """返回页面html文本"""
        if self._mode == 's':
            return super().html
        elif self._mode == 'd':
            return super(SessionPage, self).html

    @property
    def json(self) -> dict:
        """当返回内容是json格式时，返回对应的字典"""
        if self._mode == 's':
            return super().json
        elif self._mode == 'd':
            return super(SessionPage, self).json

    @property
    def response(self) -> Response:
        """返回 s 模式获取到的 Response 对象，切换到 s 模式"""
        self.change_mode('s')
        return self._response

    @property
    def mode(self) -> str:
        """返回当前模式，'s'或'd' """
        return self._mode

    @property
    def cookies(self):
        if self._mode == 's':
            return super().get_cookies()
        elif self._mode == 'd':
            return super(SessionPage, self).get_cookies()

    @property
    def session(self) -> Session:
        """返回Session对象，如未初始化则按配置信息创建"""
        if self._session is None:
            self._set_session(self._session_options)

            # if self._proxy:
            #     self._session.proxies = self._proxy

        return self._session

    @property
    def driver(self) -> Tab:
        """返回Tab对象，如未初始化则按配置信息创建。         \n
        如设置了本地调试浏览器，可自动接入或打开浏览器进程。
        """
        self.change_mode('d')
        if self._driver is None:
            self._connect_debugger(self._driver_options, self._setting_handle)

        return self._driver

    @property
    def _session_url(self) -> str:
        """返回 session 保存的url"""
        return self._response.url if self._response else None

    def get(self,
            url: str,
            show_errmsg: bool = False,
            retry: int = None,
            interval: float = None,
            timeout: float = None,
            **kwargs) -> Union[bool, None]:
        """跳转到一个url                                         \n
        :param url: 目标url
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param timeout: 连接超时时间（秒）
        :param kwargs: 连接参数，s模式专用
        :return: url是否可用，d模式返回None时表示不确定
        """
        if self._mode == 'd':
            return super(SessionPage, self).get(url, show_errmsg, retry, interval, timeout)
        elif self._mode == 's':
            return super().get(url, show_errmsg, retry, interval, timeout, **kwargs)

    def ele(self,
            loc_or_ele: Union[Tuple[str, str], str, ChromeElement, SessionElement],
            timeout: float = None) -> Union[ChromeElement, SessionElement, str, None]:
        """返回第一个符合条件的元素、属性或节点文本                               \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与页面等待时间一致
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super().ele(loc_or_ele)
        elif self._mode == 'd':
            return super(SessionPage, self).ele(loc_or_ele, timeout=timeout)

    def eles(self,
             loc_or_str: Union[Tuple[str, str], str],
             timeout: float = None) -> List[Union[ChromeElement, SessionElement, str]]:
        """返回页面中所有符合条件的元素、属性或节点文本                                \n
        :param loc_or_str: 元素的定位信息，可以是loc元组，或查询字符串
        :param timeout: 查找元素超时时间，默认与页面等待时间一致
        :return: 元素对象或属性、文本组成的列表
        """
        if self._mode == 's':
            return super().eles(loc_or_str)
        elif self._mode == 'd':
            return super(SessionPage, self).eles(loc_or_str, timeout=timeout)

    def change_mode(self, mode: str = None, go: bool = True) -> None:
        """切换模式，接收's'或'd'，除此以外的字符串会切换为 d 模式     \n
        切换时会把当前模式的cookies复制到目标模式                   \n
        切换后，如果go是True，调用相应的get函数使访问的页面同步        \n
        注意：s转d时，若浏览器当前网址域名和s模式不一样，必须会跳转      \n
        :param mode: 模式字符串
        :param go: 是否跳转到原模式的url
        """
        if mode is not None and mode.lower() == self._mode:
            return

        self._mode = 's' if self._mode == 'd' else 'd'

        # s模式转d模式
        if self._mode == 'd':
            if not self._has_driver:
                self._ready()
            self._has_driver = True
            self._url = None if not self._has_driver else super(SessionPage, self).url

            if self._session_url:
                self.cookies_to_driver()

                if go:
                    self.get(self._session_url)

        # d模式转s模式
        elif self._mode == 's':
            self._has_session = True
            self._url = self._session_url

            if self._has_driver:
                self.cookies_to_session()

                if go:
                    url = super(SessionPage, self).url
                    if url.startswith('http'):
                        self.get(url)

    def cookies_to_session(self, copy_user_agent: bool = False) -> None:
        """把driver对象的cookies复制到session对象    \n
        :param copy_user_agent: 是否复制ua信息
        :return: None
        """
        if copy_user_agent:
            selenium_user_agent = self.run_script("navigator.userAgent;")
            self.session.headers.update({"User-Agent": selenium_user_agent})

        self.set_cookies(super(SessionPage, self).get_cookies(as_dict=True), set_session=True)

    def cookies_to_driver(self) -> None:
        """把session对象的cookies复制到driver对象"""
        ex_url = extract(self._session_url)
        domain = f'{ex_url.domain}.{ex_url.suffix}'
        cookies = []
        for cookie in super().get_cookies():
            if cookie.get('domain', '') == '':
                cookie['domain'] = domain

            if domain in cookie['domain']:
                cookies.append(cookie)
        self.set_cookies(cookies, set_driver=True)

    def get_cookies(self, as_dict: bool = False, all_domains: bool = False) -> Union[dict, list]:
        """返回cookies                               \n
        :param as_dict: 是否以字典方式返回
        :param all_domains: 是否返回所有域的cookies
        :return: cookies信息
        """
        if self._mode == 's':
            return super().get_cookies(as_dict, all_domains)
        elif self._mode == 'd':
            return super(SessionPage, self).get_cookies(as_dict)

    def set_cookies(self, cookies, set_session: bool = False, set_driver: bool = False):
        # 添加cookie到driver
        if set_driver:
            super(SessionPage, self).set_cookies(cookies)

        # 添加cookie到session
        if set_session:
            cookies = _cookies_to_tuple(cookies)
            for cookie in cookies:
                if cookie['value'] is None:
                    cookie['value'] = ''

                kwargs = {x: cookie[x] for x in cookie
                          if x.lower() in ('version', 'port', 'domain', 'path', 'secure',
                                           'expires', 'discard', 'comment', 'comment_url', 'rest')}

                if 'expiry' in cookie:
                    kwargs['expires'] = cookie['expiry']

                self.session.cookies.set(cookie['name'], cookie['value'], **kwargs)

    # ----------------重写SessionPage的函数-----------------------
    def post(self,
             url: str,
             data: Union[dict, str] = None,
             show_errmsg: bool = False,
             retry: int = None,
             interval: float = None,
             **kwargs) -> bool:
        """用post方式跳转到url，会切换到s模式                        \n
        :param url: 目标url
        :param data: post方式时提交的数据
        :param show_errmsg: 是否显示和抛出异常
        :param retry: 重试次数
        :param interval: 重试间隔（秒）
        :param kwargs: 连接参数
        :return: url是否可用
        """
        self.change_mode('s', go=False)
        return super().post(url, data, show_errmsg, retry, interval, **kwargs)

    @property
    def download(self) -> DownloadKit:
        if self.mode == 'd':
            self.cookies_to_session()
        return super().download

    def _ele(self,
             loc_or_ele: Union[Tuple[str, str], str, ChromeElement, SessionElement],
             timeout: float = None, single: bool = True) \
            -> Union[ChromeElement, SessionElement, str, None, List[Union[SessionElement, str]], List[
                Union[ChromeElement, str]]]:
        """返回页面中符合条件的元素、属性或节点文本，默认返回第一个                                               \n
        :param loc_or_ele: 元素的定位信息，可以是元素对象，loc元组，或查询字符串
        :param timeout: 查找元素超时时间，d模式专用
        :param single: True则返回第一个，False则返回全部
        :return: 元素对象或属性、文本节点文本
        """
        if self._mode == 's':
            return super()._ele(loc_or_ele, single=single)
        elif self._mode == 'd':
            return super(SessionPage, self)._ele(loc_or_ele, timeout=timeout, single=single)

    def _set_session(self, data: dict) -> None:
        """根据传入字典对session进行设置    \n
        :param data: session配置字典
        :return: None
        """
        if self._session is None:
            self._session = Session()

        if 'headers' in data:
            self._session.headers = CaseInsensitiveDict(data['headers'])
        if 'cookies' in data:
            self.set_cookies(data['cookies'], set_session=True)

        attrs = ['auth', 'proxies', 'hooks', 'params', 'verify',
                 'cert', 'stream', 'trust_env', 'max_redirects']  # , 'adapters'
        for i in attrs:
            if i in data:
                self._session.__setattr__(i, data[i])

    def _set_driver_options(self, Tab_or_Options):
        """处理driver设置"""
        if Tab_or_Options is None:
            self._driver_options = DriverOptions()

        elif Tab_or_Options is False:
            self._driver_options = DriverOptions(read_file=False)

        elif isinstance(Tab_or_Options, Tab):
            self._driver = Tab_or_Options
            self._connect_debugger(Tab_or_Options.id)
            self._has_driver = True

        elif isinstance(Tab_or_Options, DriverOptions):
            self._driver_options = Tab_or_Options

        else:
            raise TypeError('driver_or_options参数只能接收WebDriver, Options, DriverOptions或False。')

    def _set_session_options(self, Session_or_Options):
        """处理session设置"""
        if Session_or_Options is None:
            self._session_options = SessionOptions().as_dict()

        elif Session_or_Options is False:
            self._session_options = SessionOptions(read_file=False).as_dict()

        elif isinstance(Session_or_Options, Session):
            self._session = Session_or_Options
            self._has_session = True

        elif isinstance(Session_or_Options, SessionOptions):
            self._session_options = Session_or_Options.as_dict()

        elif isinstance(Session_or_Options, dict):
            self._session_options = Session_or_Options

        else:
            raise TypeError('session_or_options参数只能接收Session, dict, SessionOptions或False。')