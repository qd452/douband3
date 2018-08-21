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


def get_total_page_num(baseurl, proxies):
    # known bug:
    # for those movie list <=15, cannot analysis, cause not paginator ....
    proxydct = proxies.get_new_proxydct()
    retry = 0
    while retry <= 100:
        try:
            print(proxydct)
            r = requests.get(baseurl, proxies=proxydct,
                             timeout=1)  # less timeout means better proxy
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


@retry(stop_max_attempt_number=5)
def _get_movie_info(proxydct, movieurl):
    movie_bp = 'https://movie.douban.com/subject/'
    if not movieurl.startswith(movie_bp):
        movieurl = movie_bp + movieurl
    r = requests.get(movieurl, proxies=proxydct)
    print("{}, {}".format(movieurl, r.status_code))
    if r.status_code == 404:
        return {'name': None,
                'director': [],
                'actor': [],
                'genre': [],
                'country': [],
                'releasedate': None,
                'rating': None,
                'mv_url': movieurl
                }
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

        try:
            movierating = soup.find('strong',
                                    attrs={"property": "v:average"}).text
        except:
            movierating = None  # 建党伟业 没有评分。。。　
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


def get_movie_info(proxydct, movieurl):
    try:
        r = _get_movie_info(proxydct, movieurl)
    except:
        r = {'name': None,
             'director': [],
             'actor': [],
             'genre': [],
             'country': [],
             'releasedate': None,
             'rating': None,
             'mv_url': movieurl
             }
    return r


def get_movie_detail(mv_urls, proxydct, retry=0):
    final_mvdetail = []

    try_c = 0
    while mv_urls:
        if try_c > retry:
            return final_mvdetail

        with ThreadPoolExecutor(max_workers=100) as executor:
            r = executor.map(partial(get_movie_info, proxydct),
                             mv_urls)

        for _ in r:
            final_mvdetail.append(_)

        mv_urls = [x.get('mv_url') for x in final_mvdetail if
                   not x.get('name')]
        final_mvdetail = [x for x in final_mvdetail if x.get('name')]
        print(mv_urls)

        try_c += 1

    return final_mvdetail


def get_user_collection(baseurl, proxies):
    pg_num, proxydct = get_total_page_num(baseurl, proxies)
    print('Total Pages are {}'.format(pg_num))
    final_mvlst = []
    print('new proxy', proxydct)

    with ThreadPoolExecutor(max_workers=30) as executor:
        r = executor.map(partial(crawl_single_page, baseurl, proxydct),
                         range(pg_num))
    for _ in r:
        final_mvlst.extend(_)  # like sort(), extend list inplace

    return final_mvlst, proxydct


def main(baseurl):
    proxies = RoProxy()
    t_start = time.time()
    collection, proxydct = get_user_collection(baseurl, proxies)
    t_end = time.time()
    print('Get Collection took {}sec'.format(t_end - t_start))
    mv_urls = [x['mv_url'] for x in collection]
    print(len(mv_urls))
    print(mv_urls[0])

    t_start = time.time()
    movie_details = get_movie_detail(mv_urls, proxydct)
    t_end = time.time()
    print('Get Movie details took {}sec'.format(t_end - t_start))
    return collection, movie_details


if __name__ == "__main__":
    baseurl = "https://movie.douban.com/people/JiaU_Dong/collect"
    #    baseurl = 'https://movie.douban.com/people/qiusebolianbo/collect'
    #    baseurl = 'https://movie.douban.com/people/150241197/collect'  # only 5 movie, cuase bug
    #    baseurl = 'https://movie.douban.com/people/122731963/collect'  # 174 movies

    proxies = RoProxy()
    t_start = time.time()
    mv, mv_detail = get_user_collection(baseurl, proxies)
    t_end = time.time()
    print('Total took {}'.format(t_end - t_start))
#    print(mv)
#    print(mv_detail)
