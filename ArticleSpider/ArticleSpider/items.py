# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose,TakeFirst
from scrapy.loader import ItemLoader
import datetime
import re
from ArticleSpider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from ArticleSpider.utils.common import extract_num


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleItemLoader(ItemLoader):
    # 自定义item，每个item的TakeFirst()统一到一起
    default_output_processor = TakeFirst()


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.strftime(datetime.datetime.now().date(), '%Y/%m/%d')

    return create_date


def get_nums(value):
    try:
        nums = re.match('.*?(\d+).*',value).group(1)
    except:
        nums = 0

    return nums

def return_value(value):
    return value


class JobboleItem(scrapy.Item):
    title = scrapy.Field()
    create_time = scrapy.Field(
        input_processor = MapCompose(date_convert)
    )
    praise = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    collect = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    comment = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    content = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    url_object_id = scrapy.Field()


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    view_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
             insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num,
               watch_user_num, view_num, crawl_time
               )
             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
             ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num),
               watch_user_num=VALUES(watch_user_num), view_num=VALUES(view_num)
         """
        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = int(self["answer_num"][0].replace(',', ''))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            view_num = int(self["watch_user_num"][1].replace(',', ''))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(',', ''))
            view_num = int(self["view_num"][1].replace(',', ''))

        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num,
                  watch_user_num, view_num, crawl_time)

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    voteup_num = scrapy.Field()
    comment_num = scrapy.Field()
    created_time = scrapy.Field()
    updated_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, voteup_num, comment_num,
              created_time, updated_time, crawl_time
              ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              ON DUPLICATE KEY UPDATE content=VALUES(content), comment_num=VALUES(comment_num), voteup_num=VALUES(voteup_num),
              updated_time=VALUES(updated_time)
        """

        created_time = datetime.datetime.fromtimestamp(self["created_time"]).strftime(SQL_DATETIME_FORMAT)
        updated_time = datetime.datetime.fromtimestamp(self["updated_time"]).strftime(SQL_DATETIME_FORMAT)
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["voteup_num"],
            self["comment_num"], created_time, updated_time,
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return insert_sql, params