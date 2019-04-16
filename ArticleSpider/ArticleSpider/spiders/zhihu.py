#! coding: utf8

import scrapy
from selenium import webdriver
from time import sleep
import base64


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowd_domains = ['www.zhihu.com/']
    start_urls = ['https://www.zhihu.com/']

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

        is_login = True
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
            browser.close()

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


    def parse(self, response):
        pass