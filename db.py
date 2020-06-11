import os
import json
import mysql.connector
from loguru import logger

class Mysql:
    def __init__(self,user,password,host,port,database):
        try:
            self.user = user
            self.password = password
            self.host = host
            self.port = port
            self.database = database
            self.connection = mysql.connector.connect(host=host,
                port=port,
                database=database,
                user=user,
                password=password)
            self.cursor = self.connection.cursor()
            self.block_domain_list = []
            self.get_all_block_domain()

        except Exception as error :
            logger.error(error)
    
    def create_table(self):
        sql_query = 'create table if not exists gj_urls ( id int NOT NULL auto_increment primary key, url varchar(700) NOT NULL UNIQUE key );'
        self.cursor.execute(sql_query)
        sql_query = 'create table if not exists gj_urls_final ( id int NOT NULL auto_increment primary key, url varchar(700) NOT NULL UNIQUE key );'
        self.cursor.execute(sql_query)
        sql_query = 'create table if not exists gj_block_domain ( id int NOT NULL auto_increment primary key, url varchar(700) NOT NULL UNIQUE key );'
        self.cursor.execute(sql_query)
        self.connection.commit()

    def check_url_crawl(self,url):
        domain = self.get_domain(url)
        if domain in self.block_domain_list:
            logger.error("Domain blocked.")
            return False

        sql_query = 'select * from gj_urls where url = "' + url + '";'
        self.cursor.execute(sql_query)
        result = self.cursor.fetchone()
        if result is None:
            sql_query = 'insert into gj_urls (url) values("'+url+'");'
            self.cursor.execute(sql_query)
            self.connection.commit()
            return True
        else:
            logger.info("-- Already crawl this url. --")
            return False            

    def save_final_url(self,url):
        sql_query = 'insert into gj_urls_final (url) values("'+url+'");'
        self.cursor.execute(sql_query)
        self.connection.commit()

    def block_domain(self,url):
        domain = self.get_domain(url)
        sql_query = 'select * from gj_block_domain where url = "' + domain + '";'
        self.cursor.execute(sql_query)
        result = self.cursor.fetchone()
        if result is None:
            self.block_domain_list.append(domain)
            sql_query = 'insert into gj_block_domain (url) values("'+domain+'");'
            self.cursor.execute(sql_query)
            self.connection.commit()

    def get_all_block_domain(self):
        sql_query = 'select * from gj_block_domain;'
        self.cursor.execute(sql_query)
        result = self.cursor.fetchall()
        for row in result:
            self.block_domain_list.append(row[1])
        logger.info("block domains count = " + str(len(self.block_domain_list)))

    def get_domain(self,url):
        spltAr = url.split("://")
        i = (0,1)[len(spltAr)>1]
        domain = spltAr[i].split("?")[0].split('/')[0].split(':')[0].lower()
        domain = domain.replace("www.","")
        return domain

    def get(self, table_name):
        try:
            sql_select_Query = 'SELECT domain_name from '+table_name+' where status != 1;'
            self.cursor.execute(sql_select_Query)
            records = self.cursor.fetchall()
            return records
        except (Exception) as error :
            logger.error(error)
    
    def set_postmeta(self,post_id,meta_key,meta_value):
        try:
            sql_query = 'INSERT INTO `wp_postmeta` (`post_id`, `meta_key`, `meta_value`) VALUES ("'+post_id+'","'+meta_key+'","'+meta_value+'");'
            self.cursor.execute(sql_query)
            self.connection.commit()
        except Exception as er:
            logger.error(er)
    

