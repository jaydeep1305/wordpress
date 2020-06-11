import re
import csv   
import sys
import json
import redis
import requests
import subprocess
from lxml import html
from loguru import logger
from bs4 import BeautifulSoup

class Ahrefs:
    def __init__(self,redis_obj,force_login):
        if force_login :
          XSRF_TOKEN = ''
          BSSESSID = ''
        else :
          if redis_obj.exists("AHREFS_XSRF_TOKEN"):
            XSRF_TOKEN = redis_obj.get("AHREFS_XSRF_TOKEN").decode()
            BSSESSID = redis_obj.get("AHREFS_BSSESSID").decode()
        self.redis_obj = redis_obj

    def login(self,USERNAME,PASSWORD):
        self.USERNAME = USERNAME
        self.PASSWORD = PASSWORD

        headers = {
            'Host': 'ahrefs.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Upgrade-Insecure-Requests': '1',
        }
        response = requests.get('https://ahrefs.com/dashboard', headers=headers, verify=True)
        response_cookie_header = response.headers['Set-Cookie']
        XSRF_TOKEN = re.search("XSRF-TOKEN=(.*?);",response_cookie_header).group(1)
        BSSESSID = re.search("BSSESSID=(.*?);",response_cookie_header).group(1)
        
        headers = {
            'Host': 'auth.ahrefs.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'text/plain;charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://ahrefs.com',
            'Referer': 'https://ahrefs.com/user/login',
        }
        data = '{"remember_me":false,"auth":{"password":"'+self.PASSWORD+'","login":"'+self.USERNAME+'"}}'
 
        cookies = {
            'XSRF-TOKEN': XSRF_TOKEN,
            'BSSESSID': BSSESSID
        }

        response = requests.post('https://auth.ahrefs.com/auth/login', headers=headers, data=data, verify=True, cookies=cookies)
        try:
            logger.info(response.content)
            json_data = (response.content).decode() 
            json_data = json.loads(json_data)
            BSSESSID = json_data['result']['session_id']
            logger.info(BSSESSID)
        except Exception as e:
            logger.error(e)
            sys.exit()

        headers = {
            'Host': 'ahrefs.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json; charset=utf-8',
            'Origin': 'https://ahrefs.com',
            'Referer': 'https://ahrefs.com/user/login',
        }
        cookies = {
            'XSRF-TOKEN': XSRF_TOKEN,
            'BSSESSID': BSSESSID
        }
        data = {"session_id":BSSESSID}
        response = requests.post('https://ahrefs.com/api/v3/auth/session/login', headers=headers, json=data,cookies=cookies, verify=True)
        logger.info(response.content)
        self.XSRF_TOKEN = XSRF_TOKEN
        self.BSSESSID = BSSESSID
        self.redis_obj.set("AHREFS_XSRF_TOKEN",self.XSRF_TOKEN)
        self.redis_obj.set("AHREFS_BSSESSID",self.BSSESSID)
        logger.info(self.XSRF_TOKEN)
        logger.info(self.BSSESSID)

    
    def serp_result(self,country,keyword):
        if self.redis_obj.exists("AHREFS_XSRF_TOKEN"):
            self.XSRF_TOKEN = self.redis_obj.get("AHREFS_XSRF_TOKEN").decode()
            self.BSSESSID = self.redis_obj.get("AHREFS_BSSESSID").decode()

        cookies = {
            'BSSESSID': str(self.BSSESSID),
            'XSRF-TOKEN': str(self.XSRF_TOKEN)
        }

        headers = {
            'Host': 'ahrefs.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json; charset=utf-8',
            'Origin': 'https://ahrefs.com',
            'Referer': 'https://ahrefs.com/user/login',
        }      
        data = {"country":country,"keyword":keyword}
        response2 = response = requests.post('https://ahrefs.com/v3/api-adaptor/keSerpOverview', headers=headers,cookies=cookies, json=data, verify=True)
        try:
            response = json.loads(response.text)
            response = response[1]
            results = response['results']
            urls = []
            for r in results:
                try:
                    try:
                        if(isinstance(r['content'][1][0][1],dict)):
                            r = r['content'][1][0][1]
                    except:
                        if(isinstance(r['content'][1],dict)):
                            r = r['content'][1]['link'][1]
                    try:
                        urls.append(r['url'])                    
                    except:
                        pass
                except Exception as ex:
                    logger.error(ex)
            return urls
        except Exception as ex:
            logger.error(response2.text)