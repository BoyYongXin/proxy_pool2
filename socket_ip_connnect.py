import socket
import threading
import time
from db import RedisClient
from loguru import logger
import requests


def testconn(host, port):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)
    try:
        sk.connect((host, port))
        return host + " Server is " + str(port) + " connect"
    except Exception:
        return host + " Server is " + str(port) + " not connect!"
    finally:
        sk.close()


def test_url(url="http://www.baidu.com", proxy=""):
    # url = "https://m.weibo.cn/p/23065700428008651010000000000?uid=7062053780&wm=20005_0002&from=10AA395010&sourcetype=weixin"
    # url = "http://www.httpbin.org/ip"
    # url = " https://m.weibo.cn/api/container/getIndex?uid=1866493240&luicode=10000011&lfid=23065700428008651010000000000&type=uid&value=1866493240&containerid=2302831866493240"
    # proxy = "222.162.220.11:10900"
    proxies = {
        "http://": "http://{proxy}".format(proxy=proxy),
        "https://": "http://{proxy}".format(proxy=proxy),
    }
    logger.info(f"测试IP : {proxies}")
    res = requests.get(url=url, proxies=proxies, timeout=10, verify=False)
    res.encoding = "urf-8"
    try:
        assert res.status_code == 201
        print(res.status_code)
        print(res.text)
    except Exception as err:
        logger.error("失效代理")
        with open("./failed_ip.txt", encoding="utf-8", mode="a+") as f:
            f.write(proxy + "\n")


class Test(threading.Thread):
    def __init__(self):
        self.redis = RedisClient(host='10.126.30.6', port=6379,
                                 redis_key="crawl:crawl_platform:proxy_pool", db=2)

    def test_conn(self, ip, port):
        return testconn(ip, port)

    def test_url(self, url="http://www.baidu.com", proxy=""):
        return test_url(url, proxy)

    def run(self):
        proxy_list = list(self.redis.smembers("crawl:crawl_platform:proxy_pool"))
        logger.info(f"共有代理IP {len(proxy_list)}")
        for proxy in proxy_list:
            '''socket-ping'''
            # proxy_ip = proxy.strip("http://").split(":")
            # result = self.test_conn(proxy_ip[0], proxy_ip[1])
            # if "not connect" in result:
            #     logger.error(result)
            # else:
            #     logger.info(result)

            self.test_url(proxy=proxy)


a = Test()
a.run()

# test_url()
