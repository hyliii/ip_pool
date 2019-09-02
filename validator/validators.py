'''
检测器：
1.添加时检测
2.速度检测
3.稳定性检测
4.定时检测
5.定量检测
6.检测循环轮次
7.判断输出
8.进程管理（主进程存取，子进程检测）
9.https/http测试
'''

import sys
import chardet
import json
import os
import gevent
import requests
import time
import psutil
from multiprocessing import Process, Queue
import config
from db.DataStore import sqlhelper
from util.exception import Test_URL_Fail
from gevent import monkey
monkey.patch_all()
def check_server(proxy):
    ip=proxy['ip']
    port=proxy['port']
    proxies = {"http": "http://%s:%s" % (ip, port), "https": "https://%s:%s" % (ip, port)}
    url1 = config.GOAL_HTTPS_LIST[0]
    url2=config.GOAL_HTTP_LIST
    c_https=requests.get(url=url1,proxies=proxies,headers=config.get_header(),timeout=config.TIMEOUT)
    c_http=requests.get(url=url2,proxies=proxies,headers=config.get_header(),timeout=config.TIMEOUT)
    if c_http and c_https:
        return 2
    elif c_https:
        return 1
    elif c_http:
        return 0
def speeds(proxys,ifhttp=True):
    urllist=config.GOAL_HTTPS_LIST
    for i in urllist:
        pass

# def new_time(proxylist,url=):
