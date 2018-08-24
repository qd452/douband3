# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 10:25:29 2018

@author: Dong.Qu
"""
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import time
from retrying import retry
from rotating_proxies import RoProxy




def get_total_page_num(baseurl, proxies):
    proxydct = proxies.get_new_proxydct()
    retry = 0
    while retry <= 30:
        try:
            print(proxydct)
            r = requests.get(baseurl, proxies=proxydct, timeout=2)
            soup = BeautifulSoup(r.content, 'html.parser')
            pg_num = int(
                soup.select(".paginator .thispage")[0]['data-total-page'])
            return pg_num, proxydct
        except Exception as e:
            proxydct = proxies.get_new_proxydct()
            retry += 1
    else:
        raise Exception('Cannot find good Proxy')
        
        
if __name__ == "__main__":
    baseurl = "https://movie.douban.com/people/JiaU_Dong/collect"
    proxies = RoProxy()
    
    mvurl = 'https://movie.douban.com/subject/26647117/'
    
    get_total_page_num(baseurl, proxies) # here is just to get a usable proxy
    proxydct = proxies.get_proxydct()
    
    r = requests.get(mvurl, proxies=proxydct, timeout=2)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    rating = soup.select('.ratings-on-weight')[0]
    