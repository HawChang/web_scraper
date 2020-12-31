#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2020/12/31 3:13 PM
# @Author : ZhangHao
# @File   : vaccine_org_name_scraper.py
# @Desc   : 

import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from web_scraper import WebScraper
from selenium.common import exceptions

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class VacOrgScraper(WebScraper):
    
    def __init__(self, **kwargs):
        super(VacOrgScraper, self).__init__(**kwargs)
        self.wait_max_num = 10
        self.click_retry_max_num = 5

    def set_share_values(self, *args, **kwargs):
        """
        设置各进程共享变量
        :param args:
        :param kwargs:
        :return:
        """
        return list()
    
    def job_creator(self, *args, **kwargs):
        """
        产生多进程的任务
        :param args:
        :param kwargs:
        :return:
        """
        # 只有这一个页面
        return [["https://gjzwfw.www.gov.cn/fwmh/healthCode/indexNucleic.do"]]
    
    def job_consumer(self, web_address, *args, **kwargs):
        """
        消耗多进程的任务
        :param args:
        :param kwargs:
        :return:
        """
        opt = webdriver.ChromeOptions()
        opt.add_argument('headless')  # 设置option,后台运行
        driver = webdriver.Chrome("./driver/chromedriver", options=opt)
        driver.get(web_address)
        # 等待加载
        time.sleep(4)

        cur_page = None
        while True:
            if cur_page is None:
            # 显示当前在第几页
                cur_page = driver.find_element_by_xpath("//a[@class='lxp']").text

            # 记录当前页
            previous_page = cur_page
            logging.warning("cur_page: {}".format(cur_page))
            
            # 提取当前页的结构名
            start_time = time.time()
            selenium_page = driver.page_source
            soup = BeautifulSoup(selenium_page, 'html.parser')
            res_list = soup.select(".ghbs td:nth-of-type(2)")
            for res in res_list:
                print("\t".join([
                    cur_page,
                    res.get_text(),
                    ]))
            #logging.warning("")
            try:
                last_page = driver.find_element_by_xpath("//div[@id='page']//a[@class='xiaye' and text()='尾页']")
            except exceptions.NoSuchElementException as e:
                # 没有尾页 说明到达尾页
                logging.warning("reach last")
                break

            # 跳转到下一页
            next_page = driver.find_element_by_xpath("//div[@id='page']//a[@class='xiaye' and text()='下一页>']")

            click_retry_num = 0
            while click_retry_num < self.click_retry_max_num:
                next_page.click()
                
                # 检查页数是否已变
                retry_num = 0
                need_click = True
                while retry_num <= self.wait_max_num:
                    retry_num += 1
                    try:
                        cur_page = driver.find_element_by_xpath("//a[@class='lxp']").text
                    except exceptions.StaleElementReferenceException as e:
                        logging.error("page extract fail")
                        break
                    
                    # 当页数不变时 再等一下
                    if cur_page == previous_page:
                        time.sleep(1)
                        logging.warning("cur page = {}, previous_page = {}, wait another 1 sec"
                                        .format(cur_page, previous_page))
                    else:
                        need_click = False
                        break
                
                if not need_click:
                    break

    
    def post_process(self, res_list, share_values, *args, **kwargs):
        """
        对结果进行最后处理
        :param res_list:
        :param share_values:
        :param args:
        :param kwargs:
        :return:
        """
        # 不作处理
        pass


if __name__ == "__main__":
    scraper = VacOrgScraper(n_jobs=1)
    scraper.run()