import os
import threading
import re
import requests
import json
import time
from loguru import logger
try:
    from urllib.parse import quote_plus as url_encode
except ImportError:
    from urllib import quote_plus as url_encode

class Crawler:
    def __init__(self,FB_COOKIE_URL,USE_FACEBOOK,parsed_obj,mysql_obj):
        self.COOKIE_FB = ""
        self.FB_COOKIE_URL = FB_COOKIE_URL
        self.parsed_obj = parsed_obj
        self.mysql_obj = mysql_obj
        self.USE_FACEBOOK = USE_FACEBOOK
        
    def get_cookie(self):
        if self.USE_FACEBOOK:
            # self.COOKIE_FB = ""
            threading.Timer(30, self.get_cookie).start()
            response = requests.get(self.FB_COOKIE_URL+"index.php/facebook_test_account/cookie_get")
            self.COOKIE_FB = response.text
            logger.info(self.COOKIE_FB)
            if(len(self.COOKIE_FB)<15) :
                logger.error("COOKIE ERROR -- BLANK SHOWING IN PANEL")
                self.get_cookie()
        else :
            self.COOKIE_FB = ""

    def decode_html(self,fb_response):
        decoded = ['>', '<', '"', '&', '\'']
        encoded = ['&gt;', '&lt;', '&quot;', '&amp;', '&#039;']
        for e, d in zip(encoded, decoded):
            fb_response = fb_response.replace(e, d)
        for e, d in zip(encoded[::-1], decoded[::-1]):
            fb_response = fb_response.replace(e, d)
        return fb_response

    def crawler_data(self,link):        
        if self.mysql_obj.check_url_crawl(link):
            try:
                if self.USE_FACEBOOK:
                    encoded_link = url_encode(link)
                    logger.info(link)
                    headers = {
                            'Host': 'developers.facebook.com',
                            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Accept-Encoding': 'deflate',
                            'Connection': 'keep-alive',
                            'Cookie': self.COOKIE_FB,
                            'Upgrade-Insecure-Requests': '1',
                            'Cache-Control': 'max-age=0',
                            'TE': 'Trailers'
                    }
                    fb_response = requests.get('https://developers.facebook.com/tools/debug/echo/?q=%s' % encoded_link, headers=headers, timeout=60)
                    cleaned_response = self.decode_html(fb_response.text)
                    # logger.info(cleaned_response)
                    #####The document returned - Cookie - CHECK####
                    if "title" not in cleaned_response:
                        logger.error("cookie expired or fb block or site block fb crawl.")
                        direct_response = requests.get(link)
                        cleaned_response = direct_response.text
                else:
                    direct_response = requests.get(link)
                    cleaned_response = direct_response.text
                
                self.parsed_obj.parse(cleaned_response)
                self.mysql_obj.save_final_url(link)

            except Exception as ex:
                logger.error("Error : " + str(ex))

