# -*- coding:utf-8 -*-
"""
实用工具
"""
from json import loads, JSONDecodeError
from threading import Thread
from time import perf_counter, sleep
from typing import Union, Tuple, List, Iterable

from pychrome import Tab

from .session_element import make_session_ele
from .easy_set import get_match_driver
from .mix_page import MixPage


class ResponseData(object):
    """返回的数据包管理类"""

    def __init__(self, response: dict, body: str):
        """初始化                               \n
        :param response: response格式化的数据
        :param body: response包含的内容
        """
        self.response = response
        self.raw_body = body
        self._json_body = None

    def __getattr__(self, item):
        return self.response.get(item, None)

    @property
    def body(self):
        """返回body内容，如果是json格式，自动进行转换，其它格式直接返回文本"""
        if self._json_body is not False and self.response.get('mimeType', None) == 'application/json':
            if self._json_body is None:
                try:
                    self._json_body = loads(self.raw_body)
                except JSONDecodeError:
                    self._json_body = False
                    return self.raw_body
            return self._json_body

        else:
            return self.raw_body


class Listener(object):
    """浏览器的数据包监听器"""

    def __init__(self, page: MixPage, tab_handle: str = None):
        """初始化                                                  \n
        :param page: MixPage对象
        :param tab_handle: 要监听的标签页的handle，不输入读取当前的
        """
        self.tab = None
        self.page = page
        self.set_tab(tab_handle)

        self.listening = False
        self.targets = True
        self.results = {}

        self._response_count = 0
        self._requestIds = {}
        self._a_response_loaded = False
        self._all_response = []  # 捕捉到的所有数据格式[(target, ResponseData), ...]

    def set_targets(self, targets: Union[str, List[str], Tuple[str], bool, None]) -> None:
        """设置要拦截的目标，可以设置多个                     \n
        :param targets: 字符串或字符串组成的列表
        :return: None
        """
        if isinstance(targets, str):
            self.targets = [targets]
        elif isinstance(targets, tuple):
            self.targets = list(targets)
        elif isinstance(targets, list) or targets is True:
            self.targets = targets
        else:
            raise TypeError('targets参数只接收字符串、字符串组成的列表、True、None')

    def set_tab(self, tab_handle: str) -> None:
        """设置要监听的标签页                                \n
        :param tab_handle: 标签页的handle
        :return: None
        """
        url = self.page.drission.driver_options.debugger_address
        if not url:
            raise RuntimeError('必须设置debugger_address参数才能使用此功能。')

        if tab_handle is None:
            tab_handle = self.page.current_tab_handle

        tab_id = tab_handle.split('-')[-1]

        tab_data = {"id": tab_id, "type": "page",
                    "webSocketDebuggerUrl": f"ws://{url}/devtools/page/{tab_id}"}

        self.tab = Tab(**tab_data)

    def listen(self, targets: Union[str, List[str], Tuple[str], bool, None] = None,
               count: int = None,
               timeout: float = None,
               asyn: bool = False) -> None:
        """拦截目标请求，直到超时或达到拦截个数，每次拦截前清空结果                                     \n
        可监听多个目标，请求url包含这些字符串就会被记录                                               \n
        :param targets: 要监听的目标字符串或其组成的列表，True监听所有，None则保留之前的目标不变
        :param count: 要记录的个数，到达个数停止监听
        :param timeout: 监听最长时间，到时间即使未达到记录个数也停止，None为无限长
        :param asyn: 是否异步执行
        :return: None
        """
        if targets:
            self.set_targets(targets)

        self.tab.Network.responseReceived = self._response_received
        self.tab.Network.loadingFinished = self._loading_finished

        self.tab.start()
        self.tab.Network.enable()
        self.listening = True
        self._response_count = 0

        if asyn:
            Thread(target=self._do_listen, args=(count, timeout)).start()
        else:
            self._do_listen(count, timeout)

    def stop(self) -> None:
        """停止监听"""
        self.listening = False

    def wait(self) -> None:
        """等等监听结束"""
        while self.listening:
            sleep(.5)

    def get_results(self, target: str = None) -> List[ResponseData]:
        """获取结果列表                                        \n
        :param target: 要获取的目标，为None时获取第一个
        :return: 结果数据组成的列表
        """
        return self.results.get(next(iter(self.results))) if target is None else self.results.get(target, None)

    def _do_listen(self,
                   count: int = None,
                   timeout: float = None) -> None:
        """执行监听                                                         \n
        :param count: 要记录的个数，到达个数停止监听
        :param timeout: 监听最长时间，到时间即使未达到记录个数也停止，None为无限长
        :return: None
        """
        t1 = perf_counter()
        while True:  # 当收到停止信号、到达须获取结果数、到时间就停止
            if not self.listening \
                    or (count is not None and self._response_count >= count) \
                    or (timeout is not None and perf_counter() - t1 >= timeout):
                break
            sleep(.5)

        self.tab.Network.responseReceived = self._null_function
        self.tab.Network.loadingFinished = self._null_function
        self.listening = False

    def steps(self, gap: int = 1) -> Iterable:
        """用于单步操作，可实现没收到若干个数据包执行一步操作（如翻页）                 \n
        于是可以根据数据包是否加载完成来决定是否翻页，无须从页面dom去判断是否加载完成     \n
        大大简化代码，提高可靠性                                                   \n
        eg: for i in listener.steps(2):                                        \n
                btn.click()                                                    \n
        :param gap: 每接收到多少个数据包触发
        :return: 用于在接收到监听目标时触发动作的可迭代对象
        """
        count = 0
        while True:
            if not self.listening:
                return

            if self._a_response_loaded:
                self._a_response_loaded = False
                count += 1
                if count % gap == 0:
                    yield self._all_response[-gap:]

    def _loading_finished(self, **kwargs):
        """请求完成时处理方法"""
        requestId = kwargs['requestId']
        target = self._requestIds.pop(requestId, None)

        if target is not None:
            response = ResponseData(target['response'], self._get_response_body(requestId))
            target = target['target']
            self._response_count += 1

            if target in self.results:
                self.results[target].append(response)
            else:
                self.results[target] = [response]

            self._all_response.append((target, response))
            self._a_response_loaded = True

    def _response_received(self, **kwargs) -> None:
        """接收到返回信息时处理方法"""
        if self.targets is True:
            self._requestIds[kwargs['requestId']] = {'target': True, 'response': kwargs['response']}

        else:
            for target in self.targets:
                if target in kwargs['response']['url']:
                    self._requestIds[kwargs['requestId']] = {'target': target, 'response': kwargs['response']}

    def _null_function(self, **kwargs) -> None:
        """空方法，用于清除绑定的方法"""
        pass

    def _get_response_body(self, requestId: str) -> str:
        """获取返回的内容                  \n
        :param requestId: 请求的id
        :return: 返回内容的文本
        """
        return self.tab.call_method('Network.getResponseBody', requestId=requestId)['body']
