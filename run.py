from init import *

if REDIS_HOST == "127.0.0.1" : 
    redis_pool = redis.BlockingConnectionPool(
            host=REDIS_HOST, 
            port=REDIS_PORT,
            password=REDIS_PASS,
            max_connections=50000,
            health_check_interval=0, 
            socket_connect_timeout=1, 
            socket_timeout=1,
            socket_keepalive=True,
            retry_on_timeout=True,
            timeout=None)
else : 
    redis_pool = redis.BlockingConnectionPool(
        host=REDIS_HOST, 
        port=REDIS_PORT,
        password=REDIS_PASS,
        connection_class=redis.SSLConnection,
        max_connections=50000,
        health_check_interval=0, 
        socket_connect_timeout=1, 
        socket_timeout=1,
        socket_keepalive=True,
        retry_on_timeout=True,
        timeout=None)

redis_obj = redis.Redis(connection_pool=redis_pool)
mysql_obj = Mysql(DB_USER,DB_PASS,DB_HOST,DB_PORT,DB_DATABASE)
mysql_obj.create_table()
wordpress_obj = Wordpress(WP_USER,WP_PASS,DOMAIN_URL)
parsed_obj = Parse(wordpress_obj,mysql_obj)
force_login = False
ahrefs_obj = Ahrefs(redis_obj,force_login)
if force_login :
    ahrefs_obj.login(AHREFS_USER,AHREFS_PASS)
    force_login = False

file_keywords = open('keywords.txt', 'r') 
keywords = file_keywords.readlines() 
for keyword in keywords: 
    keyword = keyword.strip()
    logger.info("----" + keyword +"-----")
    urls = ahrefs_obj.serp_result("us",keyword)
    for url in urls:
        logger.info(url)
        crawler_obj = Crawler(FB_COOKIE_URL,USE_FACEBOOK,parsed_obj,mysql_obj)
        crawler_obj.get_cookie()
        crawler_obj.crawler_data(url)
