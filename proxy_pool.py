#! /usr/bin/env python
# -*- coding:utf-8 -*-
import re
import requests
from lxml import etree
import sqlite3
import datetime
import logging
from multiprocessing import cpu_count
from multiprocessing.dummy import Pool

requests.packages.urllib3.disable_warnings()
db = "ts.db"

def proxy_kuaidaili(page=10):
    """
    fetch from http://www.kuaidaili.com/
    """
    url_list = ('http://www.kuaidaili.com/proxylist/{page}/'.format(page=page) for page in range(1, page + 1))
    for url in url_list:
        html = requests.get(url=url).content
        tree = etree.HTML(html)
        proxy_list = tree.xpath('.//div[@id="index_free_list"]//tbody/tr')
        for proxy in proxy_list:
            yield ':'.join(proxy.xpath('./td/text()')[0:2])


def proxy_66ip(proxy_number=100):
    """
    fetch from http://www.66ip.cn/
    """
    url = "http://m.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=".format(proxy_number)
    html = requests.get(url).content.decode("GBK")
    for proxy in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html):
        yield proxy


def proxy_youdaili(days=1):
    """
    fetch from http://www.youdaili.net/Daili/http/
    """
    url = "http://www.youdaili.net/Daili/http/"
    html = requests.get(url=url).content
    tree = etree.HTML(html)
    page_url_list = tree.xpath('.//div[@class="chunlist"]/ul//a/@href')[0:days]
    for page_url in page_url_list:
        html = requests.get(page_url).content.decode("utf-8")
        proxy_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html)
        for proxy in proxy_list:
            yield proxy


def proxy_xicidaili():
    """
    fetch from http://api.xicidaili.com/free2016.txt
    """
    url = "http://api.xicidaili.com/free2016.txt"
    html = requests.get(url).content.decode("utf-8")
    for proxy in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html):
        yield proxy


def proxy_guobanjia():
    """
    fetch from http://www.goubanjia.com/free/gngn/index.shtml
    """
    url = "http://www.goubanjia.com/free/gngn/index.shtml"
    html = requests.get(url=url).content.decode("utf-8")
    tree = etree.HTML(html)
    proxy_list = tree.xpath('.//td[@class="ip"]')
    for proxy in proxy_list:
        tmp = proxy.xpath(".//*[not(self::p)]/text()")
        yield ''.join(tmp[:-1]) + ":" + tmp[-1]


def save_proxy(proxy):
    proxies = {"http": "http://{proxy}".format(proxy=proxy)}
    try:
        r = requests.get('https://www.baidu.com/', proxies=proxies, timeout=20, verify=False)
        if r.status_code == 200:
            insert_into_database(db, proxy, r.elapsed.total_seconds())
        else:
            logging.info("slow or bad proxy %s , drop" % proxy)
    except Exception as e:
        logging.exception(e)


def create_database(name):
    conn = sqlite3.connect(name)
    c = conn.cursor()
    c.execute("create table ip_pool(proxy_name varchar(20) unique, proxy_response float(6), update_time timestamp)")
    logging.info("creating database %s.db " % name)
    conn.commit()
    conn.close()


def insert_into_database(name, proxy_name, proxy_response):
    conn = sqlite3.connect(name)
    c = conn.cursor()
    n = datetime.datetime.now()
    c.execute("insert or ignore into ip_pool(proxy_name, proxy_response, update_time) values(?,?,?)",(proxy_name, proxy_response, n))
    logging.info("save proxy %s " % proxy_name)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    logging.basicConfig(filename=now+'.log',level=logging.INFO)
    db = now + ".db"
    create_database(db)
    pool = Pool(cpu_count())
    proxy_sites = [proxy_66ip, proxy_guobanjia, proxy_kuaidaili, proxy_xicidaili, proxy_youdaili]
    for proxy_site in proxy_sites:
        try:
            pool.map(save_proxy, proxy_site())
        except Exception as e:
            logging.exception(e)
    print("finish get proxy, data saved in %s" % db)

