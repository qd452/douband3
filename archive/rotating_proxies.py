#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 18:13:44 2018

@author: qudong
"""
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import requests

class RoProxy:
    def __init__(self, anonymity="elite proxy", https="yes"):
        ua = UserAgent() # From here we generate a random user agent
        self._proxies = [] # Will contain proxies [ip, port]
        self.prx, self.prx_idx = None, None
        
        headers = {'User-Agent': ua.random}
        r = requests.get('https://www.sslproxies.org/', headers=headers)
        
        soup = BeautifulSoup(r.content, 'html.parser')
        proxies_table = soup.find(id='proxylisttable')
        # Save proxies in the array
        for row in proxies_table.tbody.find_all('tr'):
            _ip, _port, _code, _country, _anonymity,\
            _google, _https, _last_checked = [x.string for x in row.find_all('td')]
            if _anonymity == anonymity and _https == https:
                self._proxies.append({
                  'ip':   _ip,
                  'port': _port
                  })
    
    def get_new_poxy(self):
        if self.prx_idx:
            del self._proxies[self.prx_idx]
        self.prx_idx = random.randint(0, len(self._proxies) - 1)
        self.prx = self._proxies[self.prx_idx]
        return self.prx
    
    def get_proxy(self):
        if self.prx:
            return self.prx
        else:
            return self.get_new_poxy()
        
    @staticmethod
    def construct_proxydct(proxy):
        proxydct = {}
        for _ in ['https', 'http']:
            proxydct[_] = "{}://{}:{}".format(_, proxy['ip'], proxy['port'])
        return proxydct
    
    def get_proxydct(self):
        proxy = self.get_proxy()
        return self.construct_proxydct(proxy)
    
    def get_new_proxydct(self):
        proxy = self.get_new_poxy()
        return self.construct_proxydct(proxy)
    
if __name__ == "__main__":
    proxies = RoProxy()
    p1 = proxies.get_new_poxy()
    p1_1 = proxies.get_proxy()
    print(p1, p1_1)
    p2 = proxies.get_new_poxy()
    print(p2)
    print(p2 in proxies._proxies)
    print(p1 in proxies._proxies)
    print(proxies.get_new_proxydct())
    print(proxies.get_proxydct())
    