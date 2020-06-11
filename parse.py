import re
from lxml import html
from loguru import logger
import json
from collections import OrderedDict
from bs4 import BeautifulSoup, Comment

class Parse:
    def __init__(self,wordpress_obj,mysql_obj) :
        self.wordpress_obj = wordpress_obj
        self.mysql_obj = mysql_obj

    def parse(self,cleaned_response):
        try :
            html = cleaned_response
            soup = BeautifulSoup(html,"lxml")
            for s in soup.select("script"):
                s.extract()
            for s in soup.select("ins"):
                s.extract()
            for s in soup.select("link"):
                s.extract()
            for s in soup.select("style"):
                s.extract()
            for s in soup.select("nav"):
                s.extract()
            for s in soup.select("figcaption"):
                s.extract()

            title = soup.find("h1",{"class":"entry-title"}).text
            meta_desc = soup.find("meta",{"name":"description"}).text

            content = soup.find("div",{"class","entry-content"})
            for element in content(text=lambda text: isinstance(text, Comment)):
                element.extract()
            
            i = 0
            for s in content.findAll("img"):
                try : 
                    src = s['src']
                    try :
                        alt = s['alt']
                    except :
                        alt = title

                    try : 
                        img_tag,temp = self.wordpress_obj.upload_image(src,alt,self.mysql_obj)
                    except Exception as ex :
                        logger.error("function error" + ex)

                    replace_tags = BeautifulSoup(img_tag,"lxml")
                    # logger.debug(img_tag)
                    s.replaceWith(replace_tags.img)
                    if i == 0 :
                        feature_image_data = temp
                    if temp is not None:
                        i += 1
                    
                except : 
                    pass

            content = content.decode()
            a_cleaner = re.compile('<a.*?>')
            content = re.sub(a_cleaner, '', content)
            a_cleaner = re.compile('</a>')
            content = re.sub(a_cleaner, '', content)
            a_cleaner = re.compile('<figure.*?>')
            content = re.sub(a_cleaner, '', content)
            a_cleaner = re.compile('</figure>')
            content = re.sub(a_cleaner, '', content)
            a_cleaner = re.compile('<p.*wp-caption.*?>.*</p>')
            content = re.sub(a_cleaner, '', content)

            if title is not None and content is not None and meta_desc is not None and feature_image_data is not None: 
                self.wordpress_obj.upload_post(title,content,feature_image_data,meta_desc,self.mysql_obj)
        
        except Exception as ex: 
            logger.error("Error - " + ex)