#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2020/12/31 2:09 PM
# @Author : ZhangHao
# @File   : web_scraper.py.py
# @Desc   :

import collections
import logging
import os  # 这个是用于文件目录操作
import shutil
import socket
import urllib
from multiprocessing import Pool, Lock, Manager


import requests
from bs4 import BeautifulSoup

#logging.getLogger(__name__).setLevel(logging.INFO)


class WebScraper(object):
    def __init__(self, socket_timeout=30, headers=None, n_jobs=10):
        # 设置socket超时时间
        socket.setdefaulttimeout(socket_timeout)
        # 设置request请求头部
        default_headers = {'User-Agent':
                               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
                               '(KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36'}
        headers = {**default_headers, **self.headers_format(headers)}
        logging.info("headers: {}".format(headers))
        
        opener = urllib.request.build_opener()
        opener.addheaders = headers.items()
        urllib.request.install_opener(opener)
        
        self.n_jobs = n_jobs

    def headers_format(self, headers):
        """
        将headers转为字典格式
        :param headers: 字典或可迭代对象
        :return: 字典格式headers
        """
        if isinstance(headers, dict):
            return headers
        elif isinstance(headers, collections.Iterable):
            return {k: v for k, v in headers}
        else:
            logging.warning("headers format fail: {}".format(headers))
            return dict()
    
    def run(self, *args, **kwargs):
        pool = Pool(self.n_jobs)
        share_values = self.set_share_values(*args, **kwargs)
        job_info_list = self.job_creator(*args, **kwargs)
        res_list = list()
        for job_info in job_info_list:
            res = pool.apply_async(self.job_consumer, args=(job_info + share_values + list(args)))
            res_list.append(res)
        pool.close()
        pool.join()
        
        res_list = [x.get() for x in res_list]
        self.post_process(res_list, share_values, *args, **kwargs)
    
    def set_share_values(self, *args, **kwargs):
        """
        设置各进程共享变量
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError
    
    def job_creator(self, *args, **kwargs):
        """
        产生多进程的任务
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError
    
    def job_consumer(self, *args, **kwargs):
        """
        消耗多进程的任务
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError
    
    def post_process(self, res_list, share_values, *args, **kwargs):
        """
        对结果进行最后处理
        :param res_list:
        :param share_values:
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError