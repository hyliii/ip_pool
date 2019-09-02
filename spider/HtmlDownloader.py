# coding:utf-8
import random
import config
import json
from db.DataStore import sqlhelper #对应datastore中的数据库类型
import requests
import chardet
"""爬虫被挂掉之后的重复爬取最大次数"""
class Html_Downloader(object):
    '''html下载器'''
    @staticmethod
    def download(url):
        try:
            r = requests.get(url=url, headers=config.get_header(), timeout=config.TIMEOUT)
            r.encoding = chardet.detect(r.content)['encoding']
            if (not r.ok) or len(r.content) < 500:
                raise ConnectionError
            else:
                return r.text
        except Exception:
            count = 0  # 已重试次数
            proxylist = sqlhelper.select(10)
            if not proxylist:
                return None
            while count < config.RETRY_TIME:
                try:
                    proxy = random.choice(proxylist)
                    ip = proxy[0]
                    port = proxy[1]
                    proxies = {"http": "http://%s:%s" % (ip, port), "https": "https://%s:%s" % (ip, port)}
                    r = requests.get(url=url, headers=config.get_header(), timeout=config.TIMEOUT, proxies=proxies)
                    r.encoding = chardet.detect(r.content)['encoding']
                    if (not r.ok) or len(r.content) < 500:
                        raise ConnectionError
                    else:
                        return r.text
                except Exception:
                    count += 1
        return None
