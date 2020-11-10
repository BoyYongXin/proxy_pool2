# -*- coding:utf-8 -*-
# @Author: Mr.Yang
# @Date: 2020/4/1 pm 2:37
# @email: 1426866609@qq.com

import asyncio
from loguru import logger
import traceback
import time
import httpx
from db import RedisClient
from settings import *
from dataclasses import dataclass
import os
import redis
import re
import requests


def run_time(fn):
    def wrapper(*args, **kwargs):
        start = time.time()
        fn(*args, **kwargs)
        logger.info(f"当前任务运行时间{time.time() - start}")

    return wrapper


def debug(func):
    def wrapper(*args, **kw):
        try:
            return func(*args, **kw)
        except Exception as err:
            logger.error(err)
            traceback.print_exc()

    return wrapper


@dataclass
class maintain_proxy(object):
    num: int = 0
    sleep_time: int = 60
    time_out: int = 5
    test_url: str = "http://www.baidu.com"
    max_keepalive_connections: int = 50
    max_connections: int = 50
    get_proxy_url: str = "https://eproxy.ppio.cloud/proxy_list?num=20"
    name: str = "ppio"
    redis = RedisClient()

    def _redis_init(self):
        try:
            if hasattr(self, 'redis') and self.redis:
                self.redis.close()
            self.redis = RedisClient()
        except redis.ConnectionError:
            self.redis = RedisClient()
            logger.warning("redis ConnectionError")

    @debug
    async def maintain_proxies(self):
        while True:
            self._redis_init()
            regex = '\.(.*?)\.'
            web_name = re.search(regex, self.test_url, re.S | re.M).group(1) + "_proxy_pool"
            proxy_num = self.redis.sget_count(self.name)
            proxy_num2 = self.redis.sget_count(web_name)
            proxy_list = list(self.redis.ssunion(self.name, web_name))


            logger.info(f"当前集合{self.name},ip总数{proxy_num}个,{web_name}集合，ip总数{proxy_num2}个，"
                        f"all_counts {proxy_num + proxy_num2}个")
            #加入了adsl 代理
            # proxy_list2 = self.redis.proxies()
            # proxy_list.extend(proxy_list2)
            if not proxy_list:
                await asyncio.sleep(TEST_CYCLE)
                continue
            await asyncio.gather(*[self.get_html(web_name, pattern) for pattern in proxy_list])
            logger.info(f"此轮校验总共{self.num}个ip，完成,暂停{TEST_CYCLE}秒， 进行下一轮的检验")
            self.num = 0
            await asyncio.sleep(TEST_CYCLE)

    async def get_html(self, name, proxy):
        proxy = proxy.replace("http://", "")
        proxies = {
            "http://": "http://{proxy}".format(proxy=proxy),
            "https://": "http://{proxy}".format(proxy=proxy),
        }
        # max_keepalive，允许的保持活动连接数或 None 始终允许。（预设10）
        # max_connections，允许的最大连接数或 None 无限制。（默认为100）
        limits = httpx.Limits(max_keepalive_connections=self.max_keepalive_connections,
                              max_connections=self.max_connections)
        try:
            async with httpx.AsyncClient(limits=limits, proxies=proxies, timeout=self.time_out) as client:
                resp = await client.get(self.test_url)
                assert resp.status_code == 200
                proxy = "http://{}".format(proxy)
                if self.redis.sadd(name, proxy):
                    logger.info(f"{proxy}, 校验成功")
                else:
                    self.redis.sdelete(name, proxy)
                    logger.error(f"{proxy}, 校验失败，不可用代理")
        except Exception as err:
            self.redis.sdelete(name, proxy)
            logger.error(f"{proxy}, err : {err}  校验失败，不可用代理")
            return
        finally:
            self.num += 1

    @debug
    async def maintain_proxies_init(self):
        """
        check proxy_pool ip
        :return:
        """
        while True:
            try:
                self._redis_init()
                regex = '\.(.*?)\.'
                # name = re.search(regex, self.get_proxy_url, re.S | re.M).group(1) + "_proxy_pool"
                name = "crawl:crawl_platform:proxy_pool"
                proxy_num = self.redis.sget_count(name)
                logger.info(f"当前集合{name},ip总数{proxy_num}个")
                proxy_list = self.redis.sget_all(name)
                headers = {}
                response = requests.get(self.get_proxy_url, headers=headers, timeout=10)
                res = response.json()
                proxy_list2 = res["proxy_list"]
                if proxy_list2:
                    for pattern in proxy_list2:
                        proxy = str(pattern["ip"]) + ":" +str(pattern["port"])
                        proxy_list.add(proxy)
                else:
                    logger.info(f"当前api——接口暂时无IP列表")
                proxy_list = list(proxy_list)
                if not proxy_list:
                    logger.info(f"api——接口ip 和 {name}池子， ip都为空,即将睡眠，稍后重启")
                    await asyncio.sleep(TEST_CYCLE)
                    continue

            except Exception as err:
                logger.error("maintain_proxies_init", err)
                logger.error(err)
                await asyncio.sleep(TEST_CYCLE)
                continue

            patterns = list(proxy_list)
            await asyncio.gather(
                *[self.get_html(name, pattern) for pattern in patterns])
            logger.info(f"此轮校验总共{self.num}个ip，完成,暂停{TEST_CYCLE}秒， 进行下一轮的检验")
            self.num = 0
            await asyncio.sleep(TEST_CYCLE)

    # @debug
    # async def maintain_proxies_ping(self):
    #     """
    #     check proxy_pool ip
    #     :return:
    #     """
    #     while True:
    #         proxy_num =self.redis.count()
    #         logger.info(f"此轮校验ip总数{proxy_num}个， 开始检验")
    #         patterns = list(redis.proxies())
    #         await asyncio.gather(*[self.ping_proxy(pattern.split(":")[0]) for pattern in patterns])
    #         logger.info(f"此轮校验完成,暂停{TEST_CYCLE}秒， 进行下一轮的检验")
    #         await asyncio.sleep(60)
    #
    # async def ping_proxy(self, proxy):
    #     """
    #     ping 主备网络
    #     :param ip:
    #     :return:
    #     """
    #     try:
    #         result = os.system(u"ping {}".format(proxy))
    #         if result == 0:
    #             logger.info(f"{proxy}, ping校验成功，可用代理")
    #             return True
    #         else:
    #             logger.error(f"{proxy}, ping校验失败，不可用代理")
    #             return False
    #     except Exception as err:
    #         logger.error(f"{proxy}, ping校验失败，不可用代理")
    #         return