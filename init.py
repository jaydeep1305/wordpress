import requests
import redis
import threading
from db import Mysql
from parse import Parse
from loguru import logger
from ahrefs import Ahrefs
from crawler import Crawler
from wordpress import Wordpress
from bounded_pool_executor import BoundedThreadPoolExecutor

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

REDIS_HOST = "redis-do-user-2970341-0.a.db.ondigitalocean.com"
REDIS_PORT = 25061
REDIS_PASS = "averf7lt1x9cca8w"
