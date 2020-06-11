import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import re

import json
import base64
import urllib.request
import ssl
import uuid
from loguru import logger
from datetime import datetime,timedelta

class Wordpress():
    def __init__(self,WP_USER,WP_PASS,DOMAIN_URL):
        self.WP_USER = WP_USER
        self.WP_PASS = WP_PASS
        self.DOMAIN_URL = DOMAIN_URL

    def check_url(self,url):
        pattern_internal_link_with_slash = '^//([^"]*)'
        if re.search(pattern_internal_link_with_slash,url):
            url = "https:" + url
        return url

    def upload_image(self,MEDIA_URL,IMG_ALT,mysql_obj):
        MEDIA_URL = self.check_url(MEDIA_URL)
        IMG_TITLE = IMG_DESC = IMG_CAPTON = IMG_ALT
        url = self.DOMAIN_URL + 'wp-json/wp/v2'
        token = base64.standard_b64encode((self.WP_USER + ':' + self.WP_PASS).encode('utf-8')) 
        headers = {'Authorization': 'Basic ' + token.decode('utf-8')}
        
        try :
            FILE_NAME = MEDIA_URL.split("?",1)[0]
            FILE_NAME = FILE_NAME.rsplit("/",1)[1]
        except Exception as ex:
            logger.error("image error - " + ex)
            FILE_NAME = uuid.uuid4().hex.upper()[0:15] + ".jpg"
        
        try:
            FILE_NAME = "images/"+FILE_NAME

            if "." in FILE_NAME:
                headers2 = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'} 
                Picture_request = requests.get(MEDIA_URL,headers=headers2) 
                if Picture_request.status_code == 200 : 
                    with open(FILE_NAME, 'wb') as f: f.write(Picture_request.content)

            media = {'file': open(FILE_NAME,'rb')} 
            image = requests.post(url + '/media', headers=headers, files=media, verify=False)
            source_url = json.loads(image.content.decode('utf-8'))['source_url']
            image_id =json.loads(image.content.decode('utf-8'))['id']
            height = json.loads(image.content.decode('utf-8'))['media_details']['height']
            width = json.loads(image.content.decode('utf-8'))['media_details']['width']

            feature_image_data = []
            feature_image_data.append(source_url)
            feature_image_data.append(width)
            feature_image_data.append(height)
            feature_image_data.append(image_id) # thumbnail id

            post = {
                'title': IMG_TITLE,
                'caption': IMG_CAPTON,
                'description': IMG_DESC
            }
            r = requests.post(url + '/media/'+str(image_id), headers=headers, json=post, verify=False)
            mysql_obj.set_postmeta(str(image_id),'_wp_attachment_image_alt',IMG_ALT)
            logger.debug(MEDIA_URL)
        except Exception as ex:
            logger.error(ex)

        try :
            img_tag = "<img class='wp-image-"+str(image_id)+"' src='"+source_url+"' alt=\""+IMG_ALT+"\"/>"
            img_data = feature_image_data

        except :
            img_tag = ""
            img_data = None

        return img_tag,img_data

    def upload_post(self,title,content,feature_image_data,meta_desc,mysql_obj):
        try :
            feature_image_url = feature_image_data[0]
            feature_image_width = feature_image_data[1]
            feature_image_width = str(feature_image_width)
            feature_image_height = feature_image_data[2]
            feature_image_height = str(feature_image_height)
            feature_image_id = feature_image_data[3]
            feature_image_id = str(feature_image_id)
            coverage_start_date = datetime.today().strftime('%Y-%m-%d')
            coverage_start_time = datetime.today().strftime('%H:%M')
            coverage_end_date = datetime.today().strftime('%Y-%m-%d')
            coverage_end_time = datetime.today() + timedelta(hours=3)
            coverage_end_time = coverage_end_time.strftime('%H:%M')

            title = title.replace("2016","2020")
            title = title.replace("2017","2020")
            title = title.replace("2018","2020")
            title = title.replace("2019","2020")

            content = content.replace("2016","2020")
            content = content.replace("2017","2020")
            content = content.replace("2018","2020")
            content = content.replace("2019","2020")

            url = self.DOMAIN_URL + 'wp-json/wp/v2'
            token = base64.standard_b64encode((self.WP_USER + ':' + self.WP_PASS).encode('utf-8')) 
            headers = {'Authorization': 'Basic ' + token.decode('utf-8')}
            post = {
                'title': str(title),
                'status': 'publish',
                'content': str(content),
                'author': '1',
                'format': 'standard'
            }

            wp_post = requests.post(url + '/posts', headers=headers, json=post, verify=False)
            post_id = json.loads(wp_post.content.decode('utf-8'))['id']
            post_link = json.loads(wp_post.content.decode('utf-8'))['link']

            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_type','articles')
            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_article_type','LiveBlogPosting')
            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_article_title',title)
            mysql_obj.set_postmeta(str(post_id),'_seopress_titles_title',title)
            mysql_obj.set_postmeta(str(post_id),'_seopress_social_fb_title',title)
            mysql_obj.set_postmeta(str(post_id),'_seopress_social_twitter_title',title)
            mysql_obj.set_postmeta(str(post_id),'_seopress_titles_desc',meta_desc)
            mysql_obj.set_postmeta(str(post_id),'_seopress_social_fb_desc',meta_desc)
            mysql_obj.set_postmeta(str(post_id),'_seopress_social_twitter_desc',meta_desc)
            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_article_img',feature_image_url)
            mysql_obj.set_postmeta(str(post_id),'_seopress_social_fb_img',feature_image_url)
            mysql_obj.set_postmeta(str(post_id),'_seopress_social_twitter_img',feature_image_url)
            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_article_img_width',feature_image_width)
            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_article_img_height',feature_image_height)
            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_article_coverage_start_date',coverage_start_date)
            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_article_coverage_start_time',coverage_start_time)
            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_article_coverage_end_date',coverage_end_date)
            mysql_obj.set_postmeta(str(post_id),'_seopress_pro_rich_snippets_article_coverage_end_time',coverage_end_time)
            mysql_obj.set_postmeta(str(post_id),'_seopress_redirections_type','301')
            mysql_obj.set_postmeta(str(post_id),'_thumbnail_id',feature_image_id)

            logger.info("Post created : " + post_link)

        except Exception as ex: 
            logger.error(ex)

