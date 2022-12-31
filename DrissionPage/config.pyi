# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from configparser import RawConfigParser
from http.cookiejar import Cookie
from typing import Any, Union, List

from requests.cookies import RequestsCookieJar
from selenium.webdriver.chrome.options import Options


class OptionsManager(object):

    def __init__(self, path: str = ...):
        self.ini_path: str = ...
        self._conf: RawConfigParser = ...
        self._paths: dict = ...
        self._chrome_options: dict = ...
        self._session_options: dict = ...

    def __text__(self) -> str: ...

    @property
    def paths(self) -> dict: ...

    @property
    def chrome_options(self) -> dict: ...

    @property
    def session_options(self) -> dict: ...

    def get_value(self, section: str, item: str) -> Any: ...

    def get_option(self, section: str) -> dict: ...

    def set_item(self, section: str, item: str, value: Any) -> OptionsManager: ...

    def save(self, path: str = ...) -> str: ...

    def save_to_default(self) -> str: ...


class SessionOptions(object):
    def __init__(self, read_file: bool = ..., ini_path: str = ...):
        self.ini_path: str = ...
        self._headers: dict = ...
        self._cookies: list = ...
        self._auth: tuple = ...
        self._proxies: dict = ...
        self._hooks: dict = ...
        self._params: dict = ...
        self._verify: bool = ...
        self._cert: Union[str, tuple] = ...
        self._adapters: str = ...
        self._stream: bool = ...
        self._trust_env: bool = ...
        self._max_redirects: int = ...

    @property
    def headers(self) -> dict: ...

    @property
    def cookies(self) -> list: ...

    @property
    def auth(self) -> tuple: ...

    @property
    def proxies(self) -> dict: ...

    @property
    def hooks(self) -> dict: ...

    @property
    def params(self) -> dict: ...

    @property
    def verify(self) -> bool: ...

    @property
    def cert(self) -> Union[str, tuple]: ...

    @property
    def adapters(self): ...

    @property
    def stream(self) -> bool: ...

    @property
    def trust_env(self) -> bool: ...

    @property
    def max_redirects(self) -> int: ...

    @headers.setter
    def headers(self, headers: dict) -> None: ...

    @cookies.setter
    def cookies(self, cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> None: ...

    @auth.setter
    def auth(self, auth: tuple) -> None: ...

    @proxies.setter
    def proxies(self, proxies: dict) -> None: ...

    @hooks.setter
    def hooks(self, hooks: dict) -> None: ...

    @params.setter
    def params(self, params: dict) -> None: ...

    @verify.setter
    def verify(self, verify: bool) -> None: ...

    @cert.setter
    def cert(self, cert: Union[str, tuple]) -> None: ...

    @adapters.setter
    def adapters(self, adapters) -> None: ...

    @stream.setter
    def stream(self, stream: bool) -> None: ...

    @trust_env.setter
    def trust_env(self, trust_env: bool) -> None: ...

    @max_redirects.setter
    def max_redirects(self, max_redirects: int) -> None: ...

    def set_headers(self, headers: dict) -> 'SessionOptions': ...

    def set_a_header(self, attr: str, value: str) -> 'SessionOptions': ...

    def remove_a_header(self, attr: str) -> 'SessionOptions': ...

    def set_proxies(self, proxies: dict) -> 'SessionOptions': ...

    def save(self, path: str = ...) -> str: ...

    def save_to_default(self) -> str: ...

    def as_dict(self) -> dict: ...


class DriverOptions(Options):

    def __init__(self, read_file: bool = ..., ini_path: str = ...):
        self.ini_path: str = ...
        self._driver_path: str = ...
        self._user_data_path: str = ...

    @property
    def driver_path(self) -> str: ...

    @property
    def chrome_path(self) -> str: ...

    @property
    def user_data_path(self) -> str: ...

    # -------------重写父类方法，实现链式操作-------------
    def add_argument(self, argument: str) -> 'DriverOptions': ...

    def set_capability(self, name: str, value: str) -> 'DriverOptions': ...

    def add_extension(self, extension: str) -> 'DriverOptions': ...

    def add_encoded_extension(self, extension: str) -> 'DriverOptions': ...

    def add_experimental_option(self, name: str, value: Union[str, int, dict, List[str]]) -> 'DriverOptions': ...

    # -------------重写父类方法结束-------------

    def save(self, path: str = ...) -> str: ...

    def save_to_default(self) -> str: ...

    def remove_argument(self, value: str) -> 'DriverOptions': ...

    def remove_experimental_option(self, key: str) -> 'DriverOptions': ...

    def remove_all_extensions(self) -> 'DriverOptions': ...

    def set_argument(self, arg: str, value: Union[bool, str]) -> 'DriverOptions': ...

    def set_timeouts(self, implicit: float = ..., pageLoad: float = ..., script: float = ...) -> 'DriverOptions': ...

    def set_headless(self, on_off: bool = ...) -> 'DriverOptions': ...

    def set_no_imgs(self, on_off: bool = ...) -> 'DriverOptions': ...

    def set_no_js(self, on_off: bool = ...) -> 'DriverOptions': ...

    def set_mute(self, on_off: bool = ...) -> 'DriverOptions': ...

    def set_user_agent(self, user_agent: str) -> 'DriverOptions': ...

    def set_proxy(self, proxy: str) -> 'DriverOptions': ...

    def set_page_load_strategy(self, value: str) -> 'DriverOptions': ...

    def set_paths(self,
                  driver_path: str = ...,
                  chrome_path: str = ...,
                  local_port: Union[int, str] = ...,
                  debugger_address: str = ...,
                  download_path: str = ...,
                  user_data_path: str = ...,
                  cache_path: str = ...) -> 'DriverOptions': ...

    def as_dict(self) -> dict: ...


def chrome_options_to_dict(options: Union[dict, DriverOptions, Options, None, bool]) -> Union[dict, None]: ...


def session_options_to_dict(options: Union[dict, SessionOptions, None]) -> Union[dict, None]: ...


def cookie_to_dict(cookie: Union[Cookie, str, dict]) -> dict: ...


def cookies_to_tuple(cookies: Union[RequestsCookieJar, list, tuple, str, dict]) -> tuple: ...
