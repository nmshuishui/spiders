#! coding: utf8

import scrapy
from selenium import webdriver
from time import sleep
import base64
try:
    import urlparse as parse
except:
    from urllib import parse
import re
import json
import datetime
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuAnswerItem,ZhihuQuestionItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowd_domains = ['www.zhihu.com/']
    start_urls = ['https://www.zhihu.com/']

    answers_api = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit={1}&offset={2}&platform=desktop&sort_by=default"

    def start_requests(self):
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.keys import Keys
        chrome_option = Options()
        chrome_option.add_argument('--disable-extensions')
        chrome_option.add_experimental_option('debuggerAddress','127.0.0.1:9222')

        browser = webdriver.Chrome(executable_path='C:/python/chromedriver.exe', chrome_options=chrome_option)

        try:
            browser.maximize_window()
        except:
            pass


        browser.get('https://www.zhihu.com')

        try:
            browser.find_element_by_class_name('PushNotifications-icon')
            is_login = True
        except:
            is_login = False

        if is_login:
            cookies = browser.get_cookies()
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
            # browser.close()

            return [scrapy.Request(url=self.start_urls[0], dont_filter=True, cookies=cookie_dict)]

        while not is_login:
            browser.get('https://www.zhihu.com/signin')
            browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper .Input').send_keys(
                Keys.CONTROL + 'a')
            browser.find_element_by_css_selector('.SignFlow-accountInput.Input-wrapper .Input').send_keys(
                '353025240@qq.com')
            browser.find_element_by_css_selector('.SignFlow-password input').send_keys(Keys.CONTROL + 'a')
            browser.find_element_by_css_selector('.SignFlow-password input').send_keys('adminadmin')
            browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
            try:
                englishImg = browser.find_element_by_class_name('Captcha-englishImg')
            except:
                englishImg = None

            try:
                chineseImg = browser.find_element_by_class_name("Captcha-chineseImg")
            except:
                chineseImg = None

            toolbar_position = browser.execute_script('return window.outerHeight - window.innerHeight;')

            if chineseImg:
                img_position = chineseImg.location
                size = chineseImg.size
                img_x = img_position['x']
                img_y = img_position['y']
                img_base64_str = chineseImg.get_attribute('src').replace('data:image/jpg;base64,','').replace("%0A", "")
                img = open('chineseImg.jpg', 'wb')
                img.write(base64.b64decode(img_base64_str))
                img.close()

                from zheye import zheye
                z = zheye()

                chinese_pos = []
                try:
                    relative_positions = z.Recognize('chineseImg.jpg')
                    if len(relative_positions) == 2:
                        if relative_positions[0][1] > relative_positions[1][1]:
                            chinese_pos.append([relative_positions[1][1], relative_positions[1][0]])
                            chinese_pos.append([relative_positions[0][1], relative_positions[0][0]])
                        else:
                            chinese_pos.append([relative_positions[0][1], relative_positions[0][0]])
                            chinese_pos.append([relative_positions[1][1], relative_positions[1][0]])

                        # 浏览器和显示器一定要设置显示为100%：控制面板\外观和个性化\显示，否则获取的坐标位置不正确
                        from mouse import move,click
                        first_x = img_x + chinese_pos[0][0] / 2
                        first_y = img_y + chinese_pos[0][1] / 2 + toolbar_position
                        move(first_x,first_y)
                        click()
                        second_x = img_x + chinese_pos[1][0] / 2
                        second_y = img_y + chinese_pos[1][1] / 2 + toolbar_position
                        move(second_x, second_y)
                        click()
                        browser.find_element_by_css_selector('.Button.SignFlow-submitButton').click()
                        # sleep一下，要不登录成功后，还没来的急跳转就获取不到登录成功的元素
                        sleep(3)
                        try:
                            browser.find_element_by_class_name('PushNotifications-icon')
                            is_login = True
                            return [scrapy.Request(url=self.start_urls[0], dont_filter=True)]
                        except:
                            is_login = False
                except OSError as e:
                    # 捕获生成的验证码图片打不开 和 1个倒立文字的情况
                    print(e)


    def parse(self, response):
        all_urls = response.css('.ContentItem-title div a::attr(href)').extract()
        for url in all_urls:
            is_match_url = re.match('(.*/question/(\d+/)).*',parse.urljoin(response.url,url))
            if is_match_url:
                request_url = is_match_url.group(1)
                yield scrapy.Request(url=request_url, callback=self.parseQuestion)
            else:
                yield scrapy.Request(url, callback=self.parse)


    def parseQuestion(self, response):
        if "QuestionHeader-title" in response.text:
            # 处理新版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)

            item_loader.add_value('zhihu_id', question_id)
            item_loader.add_css('topics', '.QuestionHeader-topics .Popover div::text')
            item_loader.add_value('url', response.url)
            item_loader.add_css('title', '.QuestionHeader-title::text')
            item_loader.add_css('content', '.QuestionAnswers-answers')
            item_loader.add_css("answer_num", ".List-headerText span::text")
            item_loader.add_css('watch_user_num', '.QuestionFollowStatus-counts button .NumberBoard-itemValue::text')
            item_loader.add_css('view_num', '.QuestionFollowStatus-counts div .NumberBoard-itemValue::text')

            question_item = item_loader.load_item()
        else:
            # 处理老版本页面的item提取
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")
            item_loader.add_value("url", response.url)
            item_loader.add_xpath("title",
                                  "//*[@id='TopstoryContent']/div/div/div/div[2]/div/div/h2/div/a/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_xpath("watch_user_num",
                                  "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css('view_num', '.QuestionFollowStatus-counts div .NumberBoard-itemValue')

            question_item = item_loader.load_item()

        yield scrapy.Request(url=self.answers_api.format(question_id, 20, 0), callback=self.parseAnswer)
        yield question_item

    def parseAnswer(self, reponse):
        answers = json.loads(reponse.text)
        next_url = answers['paging']['next']
        is_end = answers['paging']['is_end']

        for answer in answers['data']:
            answer_item = ZhihuAnswerItem()
            answer_item['zhihu_id'] = answer['id']
            answer_item['url'] = answer['url']
            answer_item['question_id'] = answer['question']['id']
            answer_item['author_id'] = answer['author']['id']
            answer_item['content'] = answer['content']
            answer_item['voteup_num'] = answer['voteup_count']
            answer_item['comment_num'] = answer['comment_count']
            answer_item['created_time'] = answer['created_time']
            answer_item['updated_time'] = answer['updated_time']
            answer_item['crawl_time'] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, callback=self.parseAnswer)