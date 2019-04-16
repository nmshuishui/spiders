# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
import codecs
import json
from scrapy.pipelines.images import ImagesPipeline

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    #采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'root', 'scrapyspider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, create_time, praise, collect, comment, content, front_image_url, front_image_path, url_object_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            item['title'], item['create_time'], item['praise'], item['collect'], item['comment'], item['content'], item['front_image_url'][0]
            , item['front_image_path'], item['url_object_id'])
        self.cursor.execute(insert_sql, params)
        self.conn.commit()

        """
            create table jobbole_article(
                title varchar(200) comment '文章标题',
                create_time date comment '创建时间',
                praise int comment '点赞数',
                collect int comment '收藏数',
                comment int comment '评论数',
                content varchar comment '文章内容',
                front_image_url varchar(100) comment '文章封面图片url',
                front_image_path varchar(100) comment '文章封面图片本地保存路径',
                url_object_id varchar(100) comment '文章url加密统一长度'
            )DEFAULT CHARSET=utf8;
        """

        # 这里return item，是因为settings.py中配置的JsonPipeline还要使用Item，否则下面的item则为None
        return item


class JsonPipeline(object):
    # 写入json文件
    def __init__(self):
        self.json_file = codecs.open('jobbole.json', 'w', encoding='utf8')

    def process_item(self, item, spider):
        """
        item 的类型是class, json.dumps()需要的类型是dict,所以先要转换下item的类型
        ensure_ascii=False, python2中可以直接查看汉字,就不是\u8001\u7801\u519c这种
        """
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.json_file.write(lines)
        return item

    def spider_closed(self):
        self.json_file.close()


class ArticleImagePipeline(ImagesPipeline):
    # 重载ImagePipeline中的item_completed方法，获取下载地址
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]   #将路径保存在item中返回
            item["front_image_path"] = image_file_path

        # 重载完pipeline的时候，一定要return回去，配置的别的pipeline还要使用
        return item