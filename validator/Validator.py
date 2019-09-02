# coding:utf-8
import sys
import chardet
from gevent import monkey
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
monkey.patch_all()
def validator(queue1, queue2, myip):
    tasklist = []
    proc_pool = {}     # 所有进程列表
    cntl_q = Queue()   # 控制信息队列
    while True:
        if not cntl_q.empty():
            # 处理已结束的进程
            try:
                pid = cntl_q.get()
                proc = proc_pool.pop(pid)
                proc_ps = psutil.Process(pid)
                proc_ps.kill()
                proc_ps.wait()
            except Exception as e:
                pass
                # print(e)
                # print(" we are unable to kill pid:%s" % (pid))
        try:
            # proxy_dict = {'source':'crawl','data':proxy}
            if len(proc_pool) >= config.MAX_CHECK_PROCESS:
                time.sleep(config.CHECK_WATI_TIME)
                continue
            proxy = queue1.get()
            tasklist.append(proxy)
            if len(tasklist) >= config.MAX_CHECK_CONCURRENT_PER_PROCESS:
                p = Process(target=process_start, args=(tasklist, myip, queue2, cntl_q))
                p.start()
                proc_pool[p.pid] = p
                tasklist = []
        except Exception as e:
            if len(tasklist) > 0:
                p = Process(target=process_start, args=(tasklist, myip, queue2, cntl_q))
                p.start()
                proc_pool[p.pid] = p
                tasklist = []
def process_start(tasks, myip, queue2, cntl):
    spawns = []
    for task in tasks:
        spawns.append(gevent.spawn(detect_proxy, myip, task, queue2))
    gevent.joinall(spawns)
    cntl.put(os.getpid())  # 子进程退出是加入控制队列

def detect_from_db(myip, proxy, proxies_set):
    proxy_dict = {'ip': proxy[0], 'port': proxy[1]}
    speed_dict={}
    result1,result2 = detect_proxy(myip, proxy_dict,speed_dict)
    if result1:
        proxy_str = '%s:%s' % (proxy[0], proxy[1])
        proxies_set.add(proxy_str)
    else:
        if proxy[2] < 1:
            sqlhelper.delete({'ip': proxy[0], 'port': proxy[1]})
        else:
            score = proxy[2]-1
            sqlhelper.update({'ip': proxy[0], 'port': proxy[1]}, {'score': score})
            proxy_str = '%s:%s' % (proxy[0], proxy[1])
            proxies_set.add(proxy_str)
def detect_proxy(selfip, proxy, speed,queue2=None):
    ip = proxy['ip']
    port = proxy['port']
    proxies = {"http": "http://%s:%s" % (ip, port), "https": "https://%s:%s" % (ip, port)}
    protocol, types, speeds = getattr(sys.modules[__name__],config.CHECK_PROXY['function'])(selfip, proxies)#checkProxy(selfip, proxies)
    if protocol >= 0:
        proxy['protocol'] = protocol
        proxy['types'] = types
    else:
        proxy = None
    if speeds:
        r_speed=[]
        for i in speeds:
            speed['ip']=ip
            speed['port']=port
            speed['t_speed']=i
            speed['company']=config.GOAL_HTTPS_LIST[speeds.index(i)]
            r_speed.append(speed)
    else:
        r_speed= None
    if queue2:
        queue2.put(proxy)
    return proxy,r_speed
def checkProxy(selfip, proxies):
    '''检测protocol，0：http,1:https,2:http/https'''
    http, http_types,speeds= _checkHttpProxy(selfip, proxies)
    https, https_types,speeds = _checkHttpProxy(selfip, proxies, False)
    if http and https:
        protocol = 2
        types = http_types
    elif http:
        types = http_types
        protocol = 0
    elif https:
        types = https_types
        protocol = 1
    else:
        types = -1
        protocol = -1
    return protocol,types,speeds
def _checkHttpProxy(selfip, proxies, isHttp=True):
    types = -1
    if isHttp:
        test_url = config.GOAL_HTTP_LIST
    else:
        test_url = config.GOAL_HTTPS_LIST
    speeds = checkSped(selfip, proxies, test_url)
    try:
        r = requests.get(url=test_url[0], headers=config.get_header(), timeout=config.TIMEOUT, proxies=proxies)
        if r.ok:
            content = json.loads(r.text)
            headers = content['headers']
            ip = content['origin']
            proxy_connection = headers.get('Proxy-Connection', None)
            if ',' in ip:
                types = 2
            elif proxy_connection:
                types = 1
            else:
                types = 0
            return True, types,speeds
        else:
            return False, types,speeds
    except Exception as e:
        return False, types,speeds
def checkSped(selfip, proxies, test_url):
    speeds = []
    try:
        for i in test_url:
            start = time.time()
            r = requests.get(url=i, headers=config.get_header(), timeout=config.TIMEOUT, proxies=proxies)
            if r.ok:
                speed = round(int(time.time() - start), 2)
                speeds.append(speed)
            else:
                speeds.append(1000000)
        return speeds
    except Exception as e:
        return speeds
def getMyIP():
    try:
        r = requests.get(url=config.TEST_IP, headers=config.get_header(), timeout=config.TIMEOUT)
        ip = json.loads(r.text)
        return ip['origin']
    except Exception as e:
        raise Test_URL_Fail
if __name__ == '__main__':
    ip = '222.186.161.132'
    port = 3128
    proxies = {"http": "http://%s:%s" % (ip, port), "https": "http://%s:%s" % (ip, port)}
    _checkHttpProxy(None,proxies)
    # getMyIP()
    # str="{ip:'61.150.43.121',address:'陕西省西安市 西安电子科技大学'}"
    # j = json.dumps(str)
    # str = j['ip']
    # print str