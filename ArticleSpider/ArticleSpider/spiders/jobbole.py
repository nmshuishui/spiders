# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
try:
    import urlparse
except:
    from urllib import parse as urlparse
import re
from ArticleSpider.items import JobboleItem
from ArticleSpider.utils.common import get_md5
import datetime
from scrapy.loader import ItemLoader
from ArticleSpider.items import JobboleItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        artical_urls = response.css('#archive .floated-thumb .post-thumb a')
        for artical_url in artical_urls:
            # href = artical_url.css("::attr(href)").extract()[0]
            href_url = artical_url.css("::attr(href)").extract_first("")
            img_url = artical_url.css("img::attr(src)").extract_first("")
            yield Request(url=urlparse.urljoin(response.url, href_url), meta={"front_image_url":img_url}, callback=self.parse_detail)

        next_page = response.css('#archive .next::attr(href)').extract_first("")
        if next_page:
            yield Request(url=urlparse.urljoin(response.url, next_page), callback=self.parse)


    def parse_detail(self, response):
        article_item = JobboleItem()

        # title = response.css(".entry-header h1::text").extract_first("")
        # create_time = re.match('.*?(\d+\/\d+\/\d+).*', response.css("p.entry-meta-hide-on-mobile::text").extract_first("").strip()).group(1)
        # praise = response.css(".post-adds .vote-post-up h10::text").extract_first("")
        # try:
        #     collect = re.match('.*?(\d+).*', response.css(".post-adds .bookmark-btn::text").extract_first("")).group(1)
        # except:
        #     collect = 0
        # try:
        #     comment = re.match('.*?(\d+).*', response.css(".post-adds a[href='#article-comment'] span::text").extract_first("")).group(1)
        # except:
        #     comment = 0
        # content = response.css("div.entry").extract_first()
        # front_image_url = response.meta.get("front_image_url", "")
        # url_object_id = get_md5(response.url)
        #
        # article_item["title"] = title
        # # article_item["create_time"] = create_time
        # # 上面的用于写入json,下面的用于写入mysql
        # article_item["create_time"] = datetime.datetime.strptime(create_time, "%Y/%m/%d").date()
        # article_item["praise"] = praise
        # article_item["collect"] = collect
        # article_item["comment"] = comment
        # article_item["content"] = content
        # article_item["front_image_url"] = [front_image_url]
        # article_item["url_object_id"] = url_object_id


        # item_loader = ItemLoader(item=JobboleItem(), response=response)
        item_loader = JobboleItemLoader(item=JobboleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_css("create_time", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_css("praise", ".post-adds .vote-post-up h10::text")
        item_loader.add_css("collect", ".post-adds .bookmark-btn::text")
        item_loader.add_css("comment", ".post-adds a[href='#article-comment'] span::text")
        item_loader.add_css("content", "div.entry")
        # item_loader.add_value("front_image_url", [response.meta.get("front_image_url", "")])
        front_image_url = response.meta.get("front_image_url", "")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_value("url_object_id", get_md5(response.url))

        article_item = item_loader.load_item()

        yield article_item