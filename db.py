# !/usr/bin/env python
# -*-coding=utf-8 -*-
import redis
import random
from settings import *
from redis import ConnectionPool, StrictRedis


class RedisClient(object):
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, redis_key=REDIS_KEY,db=DB):
        """
        初始化Redis连接
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis 密码
        :param redis_key: Redis 哈希表名
        """
        self.pool = redis.ConnectionPool(host=host, port=port, password=password,db=db, max_connections=20,
                                         decode_responses=True)
        self.db = redis.StrictRedis(connection_pool=self.pool)
        # self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
        self.redis_key = redis_key

    def set(self, name, proxy):
        """
        设置代理
        :param name: 主机名称
        :param proxy: 代理
        :return: 设置结果
        """
        return self.db.hset(self.redis_key, name, proxy)

    def get(self, name):
        """
        获取代理
        :param name: 主机名称
        :return: 代理
        """
        return self.db.hget(self.redis_key, name)

    def count(self):
        """
        获取代理总数
        :return: 代理总数
        """
        return self.db.hlen(self.redis_key)

    def remove(self, name):
        """
        删除代理
        :param name: 主机名称
        :return: 删除结果
        """
        return self.db.hdel(self.redis_key, name)

    def names(self):
        """
        获取主机名称列表
        :return: 获取主机名称列表
        """
        return self.db.hkeys(self.redis_key)

    def proxies(self):
        """
        获取代理列表
        :return: 代理列表
        """
        return self.db.hvals(self.redis_key)

    def random(self):
        """
        随机获取代理
        :return:
        """
        proxies = self.proxies()
        return random.choice(proxies)

    def all(self):
        """
        获取字典
        :return:
        """
        return self.db.hgetall(self.redis_key)

    def close(self):
        """
        关闭 Redis 连接
        :return:
        """
        del self.db

    def sadd(self, table, values):
        '''
        @summary: 使用无序set集合存储数据， 去重
        ---------
        @param table:
        @param values: 值； 支持list 或 单个值
        ---------
        @result: 若库中存在 返回0，否则入库，返回1。 批量添加返回None
        '''
        return self.db.sadd(table, values)

    def sget_all(self, name):
        return self.db.smembers(name)

    def sget(self, table, count=0):
        datas = self.db.srandmember(table, count)
        return datas

    def sget_count(self, table):
        return self.db.scard(table)

    def sdelete(self, table, item):
        return self.db.srem(table, item)

    def sget_random(self, table, count=1):
        return self.db.srandmember(table, count)

    def ssunion(self, set1, set2):
        """
        求两个集合的补集
        :param set1:
        :param set2:
        :return:
        """
        return self.db.sunion(set1, set2)
    def smembers(self,table):
        return self.db.smembers(table)


if __name__ == '__main__':
    redis = RedisClient()
    table = "baidu"
    if redis.sadd(table, "192.168.1.107:3333"):
        print('www')

    a = redis.sget_all(table)
    print(a)
    print(list(a))
    print(type(a))

    q = ['adsdd', '192.168.1.107:3333']
    ss = ['adsdd', '192.168.1.107:3333']
    q.extend(ss)
    print(q)
