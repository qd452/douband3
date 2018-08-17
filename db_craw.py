#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 23:24:51 2018

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


# print(proxydct)

# urlappending = "?start=1140&sort=time&rating=all&filter=all&mode=grid"
#
# r = requests.get(url)
#
# soup = BeautifulSoup(r.content, 'html.parser')
#
# soup.select(".grid-view .item")[0]
#
# url = soup.select(".grid-view .item .title")[0].a['href']
#
# name = soup.select(".grid-view .item .title")[0].em.string
# name = soup.select(".grid-view .item .title")[0].em.contents[0]


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


@retry(stop_max_attempt_number=5)
def crawl_single_page(baseurl, proxydct, page_num):
    mvlst_sp = []
    url = baseurl + "?start={}&sort=time&rating=all&filter=all&mode=grid".format(
        15 * page_num)
    #    print(url)
    try:
        r = requests.get(url, proxies=proxydct)
    except Exception as e:
        #        print(e)
        raise e

    soup = BeautifulSoup(r.content, 'html.parser')
    mvinfo = soup.select(".grid-view .item .info")
    for mv in mvinfo:
        mv_url = mv.select(".title a")[0]['href']
        name = mv.select(".title em")[0].string
        rating = mv.find("span", attrs={"class": re.compile("rating*")})
        if rating:
            rating_user = int(rating['class'][0][6])
        else:
            rating_user = None
        date_view = mv.find("span", attrs={"class": "date"}).string

        mvlst_sp.append({"mv_url": mv_url,
                         "name": name,
                         "rating_my": rating_user,
                         "date_view": date_view})
    #    print([x['name'] for x in mvlst])
    return mvlst_sp


def seq_crawl(baseurl):
    mvlst = []
    mvinfo = True
    i = 0
    while mvinfo:
        url = baseurl + "?start={}&sort=time&rating=all&filter=all&mode=grid".format(
            15 * i)
        #        print(url)
        r = requests.get(url, proxies=proxydct)
        i += 1
        soup = BeautifulSoup(r.content, 'html.parser')
        mvinfo = soup.select(".grid-view .item .info")
        if mvinfo:
            for mv in mvinfo:
                #    mv = soup.select(".grid-view .item .info")[0]
                mv_url = mv.select(".title a")[0]['href']
                name = mv.select(".title em")[0].string
                #    rating = int(mv.findAll("span", attrs={"class": lambda x: x.startswith("rating")})[0]['class'][0][6])
                rating = mv.find("span", attrs={"class": re.compile("rating*")})
                if rating:
                    rating_user = int(rating['class'][0][6])
                else:
                    rating_user = None
                date_view = mv.find("span", attrs={"class": "date"}).string

                mvlst.append({"mv_url": mv_url,
                              "name": name,
                              "rating_my": rating_user,
                              "date_view": date_view})
        else:
            break
    #        print([x['name'] for x in mvlst])
    return mvlst


def test_threadpool():
    def foo(a, b):
        return [a] * b

    rslt = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        r = executor.map(partial(foo, 3), range(10))

        for _ in r:
            rslt.extend(_)

    return rslt


def crawl_movelist(baseurl, proxies):
    pg_num, proxydct = get_total_page_num(baseurl, proxies)
    print('Total Pages are {}'.format(pg_num))
    final_mvlst = []
    print('new proxy', proxydct)

    with ThreadPoolExecutor(max_workers=30) as executor:
        r = executor.map(partial(crawl_single_page, baseurl, proxydct),
                         range(pg_num))
        for _ in r:
            #            print(_)
            final_mvlst.extend(_)  # like sort(), extend list inplace

    return final_mvlst


def main(baseurl):
    proxies = RoProxy()
    t_start = time.time()
    r = crawl_movelist(baseurl, proxies)
    t_end = time.time()
    print('Total took {}'.format(t_end - t_start))
    # print(r)
    return r


if __name__ == "__main__":
    baseurl = "https://movie.douban.com/people/JiaU_Dong/collect"

    proxies = RoProxy()
    t_start = time.time()
    r = crawl_movelist(baseurl, proxies)
    t_end = time.time()
    print('Total took {}'.format(t_end - t_start))
    print(r)
