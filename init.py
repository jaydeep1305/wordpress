import requests
import redis
from db import Mysql
from wordpress import Wordpress
from loguru import logger
from crawler import Crawler
from parse import Parse
from ahrefs import Ahrefs
AHREFS_USER = "jds6855@gmail.com"
AHREFS_PASS = "nopassword1305"

DOMAIN_URL = "https://bestfatherday.com/"
WP_USER = 'savan'
WP_PASS = 'YUpg zdIe nIv2 XPWn U3pP 7K0L' 

DB_USER = "root"
DB_PASS = "nopassword1305"
DB_HOST = "142.93.252.83"
DB_PORT = "3306"
DB_DATABASE = "site_myfathersday"

FB_COOKIE_URL = "http://161.35.32.44:1305/"
RAW_TOPIC = "google-urls"
USE_FACEBOOK = False

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASS = ""
