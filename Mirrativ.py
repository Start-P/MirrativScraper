import random
import requests
import sys
import threading
from ua_parser import user_agent_parser
import time
import re
import string
import socket
from yarl import URL
from flask import Flask

with open('workingproxy.txt') as f:
    proxy = f.read().splitlines()

def headergen():
      ua = "UA"
      parsed_ua = user_agent_parser.Parse(ua)
      locale = random.choice(['ja-JP','en-US'])
      headers = {
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
          'Accept-Encoding': 'gzip, deflate, br',
          "Accept-language": '{},{};q=0.9'.format(locale, locale.split('-')[0]),
          'Cache-Control': 'max-age=0',
          "Sec-Ch-Ua": '" Not A;Brand";v="99", "Chromium";v="{0}", "Google Chrome";v="{0}"'.format(parsed_ua['user_agent']['major']),
          "Sec-Ch-Ua-Mobile": '?0',
          "Sec-Ch-Ua-Platform": '"{}"'.format(parsed_ua['os']['family']),
          'Connection': 'keep-alive',
          "Sec-fetch-dest": "document",
          "Sec-fetch-mode": "navigate",
          "Sec-fetch-site": "none",
          'User-Agent':ua,
          'referer': "https://google.com"
      }
      return headers

def getcsrftoken(url, session, proxies=None):
    if proxies:
        result = session.get(url, headers=headergen(), proxies=proxies).text
    else:
        result = session.get(url, headers=headergen()).text
    token = re.findall('    <meta name="csrf-token" content=".+" />', result)[0].split('"')
    return token[-2]

def getlive(url, delay, proxybool=False):
    while True:
        live_id = url.split('/')[-1]
        session = requests.Session()
        if proxybool:
            proxies = {'http': 'http://'  + random.choice(proxy), }
            token = getcsrftoken(url, session, proxies)
        else:
            token = getcsrftoken(url, session)
        headers = headergen()
        headers.update({'x-csrf-token': token, "x-timezone": "Asia/Tokyo"})
        if proxybool:
            proxies = {'http': 'http://'  + random.choice(proxy)}
            r = session.get(f'https://www.mirrativ.com/api/live/live?live_id={live_id}', headers=headers, proxies=proxies)
        else:
            r = session.get(f'https://www.mirrativ.com/api/live/live?live_id={live_id}', headers=headers)
        if 'エラー' in r.text:
            print(r.json()['status']['error'])
        else:
            try:
                print(f'現在同接: {r.json()["online_user_num"]} 最大同接: {r.json()["max_online_viewer_num"]}')
            except KeyError:
                print('err')
        time.sleep(int(random.randint(1, delay)))
