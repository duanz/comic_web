from __future__ import absolute_import

import logging
import re
import random

import requests
from celery.decorators import periodic_task
from django.core.cache import cache
from pyquery import PyQuery as pq

SECOND = 1
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24


@periodic_task(run_every=MINUTE*30)
def cache_proxy_ip_list():
    logging.debug("get proxy ip list start ")
    url = "http://www.superfastip.com/welcome/freeIP"
    res = requests.get(url)
    doc = pq(res.text)
    tbody = doc("div.row:nth-child(3) > div:nth-child(1) > table:nth-child(4) > tbody:nth-child(2)")
    tr_list = tbody.find('tr')

    ips = []
    for tr in tr_list:
        text = tr.text_content()
        ip = re.match('\d+.\d+.\d+.\d+', text)
        if ip:
            ip = ip.group()
        else:
            continue
        port = re.search("\n +\d+\n", text).group().replace('\n', '').replace(" ", '')
        h_type = re.search("HTTPS?", text).group().lower()
        ips.append({h_type: ":".join([ip, port])})

    ok_ips = available_ip(ips)
    # 存储到缓存
    cache.delete('proxy_ips')
    cache.set("proxy_ips", ok_ips)
    logging.debug("proxy ip list: {}".format(ok_ips))
    logging.debug("set proxy ip list to cache finished")
    return cache.get('proxy_ips')


def proxy_get_url(url, proxies):
    # proxies = {}
    # proxies["https"] = prox
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
               }
    response = requests.get(url, headers=headers,
                            proxies=proxies, verify=False, timeout=3)
    html_str = response.text
    return html_str


def available_ip(ip_list):
    ips = []
    for ip in ip_list:
        try:
            proxy_get_url('https://www.baidu.com/', ip)
        except TimeoutError:
            continue
        ips.append(ip)
    return ips
