# -*- encoding: utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from subprocess import Popen
from typing import Union

from requests import Session
from requests.cookies import RequestsCookieJar
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from .config import SessionOptions, DriverOptions


class Drission(object):

    def __init__(self,
                 driver_or_options: Union[RemoteWebDriver, Options, DriverOptions, bool] = ...,
                 session_or_options: Union[Session, dict, SessionOptions, bool] = ...,
                 ini_path: str = ...,
                 proxy: dict = ...):
        self._session: Session = ...
        self._session_options: dict = ...
        self._proxy: dict = ...
        self._driver: WebDriver = ...
        self._debugger: Popen = ...
        self._driver_options: DriverOptions = ...

    def __del__(self): ...

    @property
    def session(self) -> Session: ...

    @property
    def driver(self) -> WebDriver: ...

    @property
    def driver_options(self) -> Union[DriverOptions, Options]: ...

    @property
    def session_options(self) -> dict: ...

    @session_options.setter
    def session_options(self, options: Union[dict, SessionOptions]) -> None: ...

    @property
    def proxy(self) -> Union[None, dict]: ...

    @proxy.setter
    def proxy(self, proxies: dict = ...) -> None: ...

    @property
    def debugger_progress(self): ...

    def kill_browser(self) -> None: ...

    def get_browser_progress_id(self) -> Union[str, None]: ...

    def hide_browser(self) -> None: ...

    def show_browser(self) -> None: ...

    def _show_or_hide_browser(self, hide: bool = ...) -> None: ...

    def set_cookies(self,
                    cookies: Union[RequestsCookieJar, list, tuple, str, dict],
                    set_session: bool = ...,
                    set_driver: bool = ...) -> None: ...

    def _set_session(self, data: dict) -> None: ...

    def cookies_to_session(self, copy_user_agent: bool = False) -> None: ...

    def cookies_to_driver(self, url: str) -> None: ...

    def close_driver(self, kill: bool = ...) -> None: ...

    def close_session(self) -> None: ...

    def close(self) -> None: ...


def user_agent_to_session(driver: RemoteWebDriver, session: Session) -> None: ...


def create_driver(chrome_path: str, driver_path: str, options: Options) -> WebDriver: ...


def get_chrome_hwnds_from_pid(pid:str) -> list: ...


def kill_progress(pid: str = ..., port: int = ...) -> bool: ...
