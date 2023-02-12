# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from os import popen
from pathlib import Path
from threading import Thread
from typing import Union, Tuple, List

from DownloadKit import DownloadKit
from requests import Session

from session_page import DownloadSetter
from .configs.chromium_options import ChromiumOptions
from .chromium_base import ChromiumBase
from .chromium_driver import ChromiumDriver
from .chromium_tab import ChromiumTab
from .configs.driver_options import DriverOptions


class ChromiumPage(ChromiumBase):

    def __init__(self,
                 addr_driver_opts: Union[str, ChromiumOptions, ChromiumDriver, DriverOptions] = None,
                 tab_id: str = None,
                 timeout: float = None):
        self._driver_options: [ChromiumDriver, DriverOptions] = ...
        self.process: popen = ...
        self._window_setter: WindowSetter = ...
        self._main_tab: str = ...
        self._alert: Alert = ...
        self._download_path: str = ...
        self._download_set: ChromiumDownloadSetter = ...
        self._browser_driver: ChromiumDriver = ...

    def _connect_browser(self,
                         addr_driver_opts: Union[str, ChromiumDriver, DriverOptions] = None,
                         tab_id: str = None) -> None: ...

    def _set_start_options(self, addr_driver_opts: Union[str, ChromiumDriver, DriverOptions], none) -> None: ...

    def _driver_init(self, tab_id: str) -> None: ...

    @property
    def browser_driver(self) -> ChromiumDriver: ...

    @property
    def tabs_count(self) -> int: ...

    @property
    def tabs(self) -> List[str]: ...

    @property
    def main_tab(self) -> str: ...

    @property
    def latest_tab(self) -> str: ...

    @property
    def process_id(self) -> Union[None, int]: ...

    @property
    def set_window(self) -> WindowSetter: ...

    @property
    def download_set(self) -> ChromiumDownloadSetter: ...

    @property
    def download(self) -> DownloadKit: ...

    @property
    def download_path(self) -> str: ...

    def get_tab(self, tab_id: str = None) -> ChromiumTab: ...

    def to_front(self) -> None: ...

    def new_tab(self, url: str = None, switch_to: bool = True) -> None: ...

    def set_main_tab(self, tab_id: str = None) -> None: ...

    def to_main_tab(self) -> None: ...

    def to_tab(self, tab_id: str = None, activate: bool = True) -> None: ...

    def _to_tab(self, tab_id: str = None, activate: bool = True, read_doc: bool = True) -> None: ...

    def wait_download_begin(self, timeout: Union[int, float] = None) -> bool: ...

    def close_tabs(self, tab_ids: Union[str, List[str], Tuple[str]] = None, others: bool = False) -> None: ...

    def close_other_tabs(self, tab_ids: Union[str, List[str], Tuple[str]] = None) -> None: ...

    def handle_alert(self, accept: bool = True, send: str = None, timeout: float = None) -> Union[str, None]: ...

    def hide_browser(self) -> None: ...

    def show_browser(self) -> None: ...

    def quit(self) -> None: ...

    def _on_alert_close(self, **kwargs): ...

    def _on_alert_open(self, **kwargs): ...


class ChromiumDownloadSetter(DownloadSetter):
    def __init__(self, page: ChromiumPage):
        self._page: ChromiumPage = ...
        self._behavior: str = ...
        self._download_th: Thread = ...
        self._session: Session = None
        self._waiting_download: bool = ...
        self._download_begin: bool = ...

    @property
    def session(self) -> Session: ...

    @property
    def _switched_DownloadKit(self) -> DownloadKit: ...

    def save_path(self, path: Union[str, Path]) -> None: ...

    def by_browser(self) -> None: ...

    def by_DownloadKit(self) -> None: ...

    def wait_download_begin(self, timeout: Union[int, float] = None) -> bool: ...

    def _cookies_to_session(self) -> None: ...

    def _download_by_DownloadKit(self, **kwargs) -> None: ...

    def _download_by_browser(self, **kwargs) -> None: ...

    def _wait_download_complete(self) -> None: ...


class Alert(object):

    def __init__(self):
        self.activated: bool = ...
        self.text: str = ...
        self.type: str = ...
        self.defaultPrompt: str = ...
        self.response_accept: str = ...
        self.response_text: str = ...


class WindowSetter(object):

    def __init__(self, page: ChromiumPage):
        self.driver: ChromiumDriver = ...
        self.window_id: str = ...

    def maximized(self) -> None: ...

    def minimized(self) -> None: ...

    def fullscreen(self) -> None: ...

    def normal(self) -> None: ...

    def size(self, width: int = None, height: int = None) -> None: ...

    def location(self, x: int = None, y: int = None) -> None: ...

    def _get_info(self) -> dict: ...

    def _perform(self, bounds: dict) -> None: ...


def show_or_hide_browser(page: ChromiumPage, hide: bool = True) -> None: ...


def get_browser_progress_id(progress: Union[popen, None], address: str) -> Union[str, None]: ...


def get_chrome_hwnds_from_pid(pid: str, title: str) -> list: ...
