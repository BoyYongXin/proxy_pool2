# -*-coding=utf-8 -*-
import sys
import asyncio
from check_proxy import maintain_proxy

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


def run_maintainer(url=""):
    """
    通过请求网站url检验ip是否可用
    :return:
    """
    loop = asyncio.get_event_loop()
    if url:
        loop.run_until_complete(maintain_proxy(test_url=url).maintain_proxies())
    else:
        loop.run_until_complete(maintain_proxy().maintain_proxies())


def run_maintainer_init(url=""):
    """
    初始化通过请求网站url检验ip是否可用
    :return:
    """
    loop = asyncio.get_event_loop()
    if url:
        loop.run_until_complete(maintain_proxy(get_proxy_url=url).maintain_proxies_init())
    else:
        loop.run_until_complete(maintain_proxy().maintain_proxies_init())

# def run_maintainer_ping():
#     """
#     通过ping ip 检验ip是否可用
#     :return: 暂不可用
#     """
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(maintain_proxy().maintain_proxies_ping())


# if __name__ == '__main__':
#     name = sys.argv[1]
#     url = sys.argv[2]
#     if name == "url":
#         run_maintainer(url)
#     else:
#         run_maintainer_init()
