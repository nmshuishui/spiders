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
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()


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