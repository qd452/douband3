#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 22:16:37 2018

@author: qudong
"""

import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import time
from retrying import retry
from rotating_proxies import RoProxy
from db_craw import get_total_page_num

baseurl = "https://movie.douban.com/people/JiaU_Dong/collect"
moveurl = 'https://movie.douban.com/subject/26588308/'
moveurl = 'https://movie.douban.com/subject/1291843/'
moveurl = 'https://movie.douban.com/subject/26842702/'
# no matter how cannot one
cannot = ['https://movie.douban.com/subject/26581040/', 
          'https://movie.douban.com/subject/26328492/', # 这个页面不登陆看不到！
          'https://movie.douban.com/subject/19944226/',
          'https://movie.douban.com/subject/2326676/',
          'https://movie.douban.com/subject/21762415/',
          'https://movie.douban.com/subject/2301027/',
          'https://movie.douban.com/subject/6727679/',
          'https://movie.douban.com/subject/4729738/',
          'https://movie.douban.com/subject/3197069/',
          'https://movie.douban.com/subject/26864144/']


def get_movie_info(proxydct, movieurl):
    movie_bp = 'https://movie.douban.com/subject/'
    if not movieurl.startswith(movie_bp):
        movieurl = movie_bp + movieurl
    r = requests.get(movieurl, proxies=proxydct)
    if r.status_code != 200:
        raise Exception(str(r.status_code))
    else:
        soup = BeautifulSoup(r.content, 'html.parser')

        info = soup.select('#info')[0]
        tolist = lambda txt: [x.strip() for x in txt.split('/')]
        moviename = soup.select('h1 span')[0].text
        try:
            director = tolist(
                info.find('span', text='导演').next_sibling.next_sibling.text)
        except:
            director = []  # 某些纪录片没有导演
        # or
        # director = [x.text for x in info.findAll('a', attrs={'rel':'v:directedBy'})]
        try:
            actor = tolist(
                info.find('span', text='主演').next_sibling.next_sibling.text)
        except:
            actor = []  # 某些纪录片咩有演员

        try:
            genre = [x.string for x in
                     info.findAll('span', attrs={"property": "v:genre"})]
        except:
            genre = []
        try:
            country = tolist(info.find('span', text='制片国家/地区:').next_sibling)
        except:
            country = []
        try:
            releasedate = info.findAll('span',
                                       attrs={
                                           'property': 'v:initialReleaseDate'})
            releasedate = [x.text for x in releasedate][0].split('(')[
                0]  # note: get only the 1st date
        except:
            releasedate = None

        movierating = soup.find('strong', attrs={"property": "v:average"}).text
        movieinfo = {'name': moviename,
                     'director': director,
                     'actor': actor,
                     'genre': genre,
                     'country': country,
                     'releasedate': releasedate,
                     'rating': movierating,
                     'mv_url': movieurl
                     }
    return movieinfo


if __name__ == "__main__":
    mvs = ['26588308', '1291843', '26842702']
    mvs = cannot
    r = []
    proxies = RoProxy()
    pg_num, proxydct = get_total_page_num(baseurl, proxies)
    for mv in mvs:
        r.append(get_movie_info(proxydct, mv))

    print(r)
