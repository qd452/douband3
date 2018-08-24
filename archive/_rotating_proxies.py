from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import random
import requests
import pandas as pd

ua = UserAgent() # From here we generate a random user agent
proxies = [] # Will contain proxies [ip, port]

headers = {'User-Agent': ua.random}
r = requests.get('https://www.sslproxies.org/', headers=headers)


dfelite = df_proxy.ix[(df_proxy['Https']=='yes')& 
                      (df_proxy['Anonymity']=='elite proxy'),['IP Address', 'Port']]

df_proxy = pd.read_html(r.text)[0]
soup = BeautifulSoup(r.content, 'html.parser')
proxies_table = soup.find(id='proxylisttable')
# Save proxies in the array
for row in proxies_table.tbody.find_all('tr'):
    ip, port, code, country, anonymity,\
    google, https, last_checked = [x.string for x in row.find_all('td')]
    if anonymity == 'elite proxy' and https == 'yes':
        proxies.append({
          'ip':   ip,
          'port': port
          })

## Choose a random proxy
#proxy_index = random_proxy()
#proxy = proxies[proxy_index]

# Main function
def main():
  # Retrieve latest proxies
  proxies_req = Request('https://www.sslproxies.org/')
  proxies_req.add_header('User-Agent', ua.random)
  proxies_doc = urlopen(proxies_req).read().decode('utf8')

  soup = BeautifulSoup(proxies_doc, 'html.parser')
  proxies_table = soup.find(id='proxylisttable')

  # Save proxies in the array
  for row in proxies_table.tbody.find_all('tr'):
    proxies.append({
      'ip':   row.find_all('td')[0].string,
      'port': row.find_all('td')[1].string
    })

  # Choose a random proxy
  proxy_index = random_proxy()
  proxy = proxies[proxy_index]

  for n in range(1, 3):
    req = Request('http://icanhazip.com')
    req.set_proxy(proxy['ip'] + ':' + proxy['port'], 'http')
    
    req1 = Request("https://movie.douban.com/people/JiaU_Dong/collect")
    req1.set_proxy(proxy['ip'] + ':' + proxy['port'], 'https')

    # Every 10 requests, generate a new proxy
    if n % 10 == 0:
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]

    # Make the call
    try:
      my_ip = urlopen(req).read().decode('utf8')
      print('#' + str(n) + ': ' + my_ip)
      dbmv = urlopen(req1).read().decode()
      print(dbmv)
    except: # If error, delete this proxy and find another one
      del proxies[proxy_index]
      print('Proxy ' + proxy['ip'] + ':' + proxy['port'] + ' deleted.')
      proxy_index = random_proxy()
      proxy = proxies[proxy_index]

# Retrieve a random index proxy (we need the index to delete it if not working)
def random_proxy():
  return random.randint(0, len(proxies) - 1)

if __name__ == '__main__':
#  main()
  pass