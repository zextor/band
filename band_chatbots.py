import re
import sys
import html
import json
import lxml
import time
import pprint
import pickle
import pathlib
import requests
import schedule
import traceback
import linecache
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

"""
    global 
"""

HEADERS_NAVER_OPENAPI = {
    "X-Naver-Client-Id": "NoujfSLD2l81XduBvJ_n",
    "X-Naver-Client-Secret": "dmE5YkAMsv"}

HEADERS_FOR_NAVER = {
    'Host': 'm.search.naver.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cookie': 'npic=kJeFBc46eB3SYIPI718hy22GYvwDUqllFZ07jD+YnDeIiZlzpDVKIEEK9HqxTtu2CA==; ASID=d270c2f1000001638c1638470000004f; nx_open_so=1; _ga=GA1.2.2134578726.1541994883; nx_ssl=2; page_uid=UudovspySAdssuEO1eGssssssJC-512286; _naver_usersession_=A/ZPVy5KPH65x3wRv2fdQA==; BMR='}


def get_pure_text(text):
    """
        'HTML Tag' or 'URL Encoded' text change to PURE TEXT
    :param Text: for changing text
    :return: Pure Text
    """
    reg_exp = re.compile(r'<.*?>')
    removed_tag = re.sub(reg_exp, '', text)
    pure_text = html.unescape(removed_tag)
    return pure_text.strip()


def refresh_browser():
    print("REFRESH")
    c = ChatBot()
    c.refresh_browser()
    pass


def briefing_weather():
    pass


def show_static_message(message):
    c = ChatBot()
    c.send_message(message)
    pass


class ChatBot(object):
    """
        class for chat service
    """

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ChatBot, cls).__new__(cls)
            print("Created ChatBot Instance", cls.instance)
        return cls.instance

    @classmethod
    def clear_instance(cls):
        if hasattr(cls, 'instance'):
            print("Deleted ChatBot Instance", cls.instance)
            del cls.instance

    # def clear_instance(cls):
    #     print("Deleted ChatBot Instance", cls.instance)
    #     del cls.instance

    def __init__(self):
        """
            for init class
        """

        print("INIT")
        self.set_alarm()
        # self.init = True
        # self.refresh = None
        # self.getdriver = None
        #self.keywords_before = set("empty_set")
        # self.rank_format = "\n1위: {}\n2위: {}\n3위: {}"
        # self.rank = ""
        # self.kyobo_title = ""
        #self.kyobo_author = ""
        #self.howmistery_title_author = ""
        #self.BeforeCmd = ""
        #self.BeforeUser = ""
        self.links = { 1: "등록안됨", 2: "등록안됨", 3: "등록안됨"}
        self.active_wordchain = False
        self.wordchain_all_answers = []
        self.wordchain_last_user_answer = ""
        self.wordchain_last_bot_answer = ""
        # drop first value
        # temp = self.query_keywords()
        # temp = self.query_new_book(None)

    def set_driver(self, adapter_web_driver):
        self.driver = adapter_web_driver  # 어댑터에서 전달받은 웹드라이버):
        self.last_message = ""
        # print("ChatBot Driver: ", self.driver)
        # print("TYPE: ", type(self.driver))
        # print("HANDLES: ", self.driver.window_handles)
        # # self.driver.get('https://band.us/band/70571287/chat/CMpQqt')

    def set_alarm(self):
        schedule.clear()
        schedule.every().day.at("06:30").do(refresh_browser)
        schedule.every().day.at("12:30").do(refresh_browser)
        schedule.every().day.at("07:30").do(briefing_weather)
        schedule.every().day.at("08:00").do(show_static_message, "좋은 하루 보내세요~ ❤")
        schedule.every().day.at("12:00").do(show_static_message, "점심 맛있게 드세요~ ❤")
        schedule.every().day.at("18:00").do(show_static_message, "여유로운 저녁 보내세요~ ❤")
        schedule.every().day.at("23:00").do(show_static_message, "고운밤 되세요~ ❤")

    def get_new_message(self):
        if self.driver.current_window_handle != self.driver.window_handles[0]:
            print("CHANG WINDOW 0")
            self.driver.switch_to.window(self.driver.window_handles[0])

        current_message = (BeautifulSoup(self.driver.page_source, 'html.parser').find('div', {'class': '_receivedMessage'})).text
        if self.last_message != current_message:
            # print("MESSAGE CHANGED '{}'-'{}'".format(self.last_message, current_message))
            self.last_message = current_message
            return True
        else:
            # print("MESSAGE NOT CHANGE")
            return False

    def work(self):
        if self.get_new_message():
            self.query(self.last_message)

        schedule.run_pending()
        pass

    def refresh_browser(self):
        self.driver.refresh()
        time.sleep(5)

    def send_message(self, text):
        if type(text) == str and len(text) > 0:
            arr_text = text.split('\n')
            arr_text2 = list(filter(None, arr_text))
            count = len(arr_text2)
            for text2 in arr_text2:
                self.driver.find_element_by_xpath('//*[@id="write_comment_view81"]').send_keys(text2)
                #print(text2)
                count = count-1
                if count is not 0:
                    self.driver.find_element_by_xpath('//*[@id="write_comment_view81"]').send_keys(Keys.LEFT_SHIFT, '\n')
                    #print("shift enter")
                else:
                    self.driver.find_element_by_xpath('//*[@id="write_comment_view81"]').send_keys('\n')
                    #print("enter")


    def query(self, text):
        """
            process chat
        :param text:
        :return: text
        """
        pos1 = text.find(':')
        pos2 = text.find(':', pos1 + 1)
        current_user_name = text[pos1 + 2:pos2 - 1]
        current_command = text[pos2 + 2:]

        # # 같은 메세지이면 패스
        # if self.BeforeCmd == current_command and self.BeforeUser == current_user_name:
        #     return ""
        # self.BeforeUser = current_user_name
        # self.BeforeCmd = current_command

        print("MESSAGE : {}".format(text))

        is_processed = True

        # if self.active_wordchain:
        #     token = get_pure_text(current_command)
        #     if len(token) == 3:
        #         if len(self.wordchain_last_bot_answer) != 0:                # 이전답의 잇기가 아니면
        #             if self.wordchain_last_bot_answer[2] != token[0]:
        #                 return "'{}' 끝말을 이어주세요.".format(self.wordchain_last_bot_answer[2])
        #
        #         if not self.is_word(token):
        #             return "'{}' 는 사전에 없는 명사네요.".format(token)
        #
        #         if token in self.wordchain_all_answers:
        #             return "'{}' 은/는 이미 사용한 명사에요!".format(token)
        #
        #         T = self.wordchain(token)
        #         if len(T) == 0:
        #             T = "제가 졌네요ㅠㅠ\n{}님이 이겼어요!".format(current_user_name)
        #             self.active_wordchain = False
        #             self.wordchain_last_user_answer = ""
        #             self.wordchain_last_bot_answer = ""
        #             self.wordchain_all_answers.clear()
        #         else:
        #             self.wordchain_last_user_answer = token
        #             self.wordchain_last_bot_answer = T
        #             self.wordchain_all_answers.append(token)
        #             self.wordchain_all_answers.append(T)
        #         return T

        if current_command == "날씨":
            print("{날씨}", end="")
            ret = "{} 님 현재날씨입니다.\n{}".format(current_user_name, self.query_weather())
            self.send_message(ret)

        elif current_command == "캡쳐":
            print("{캡쳐}", end="")
            self.capture_screen()

        elif current_command == "누구":
            print("{캡쳐}", end="")
            self.call_member(current_user_name)

        elif current_command == "뽀봇":
            print("{핑퐁}", end="")
            self.send_message("네! " + current_user_name + "님")

        elif current_command == "빨리":
            refresh_browser()
            print("[call refresh_browser()]")
            self.send_message("빨리!! 읏쌰읏쌰!!")

        elif current_command in ["시청률", "시청율", "드라마", "예능"]:
            print("{시청률}", end="")
            l = self.query_tv_rating()
            self.send_message(current_user_name + "님 실시간 시청율입니다.")
            self.send_message(l)

        elif current_command.endswith(" 뜻"):
            print("{사전}", end="")
            Word = current_command[:-2]
            T = self.get_dic(current_user_name, Word)
            self.send_message(T)

        elif current_command.endswith(" 검색"):
            print("{검색}", end="")
            Word = current_command[:-3]
            T = self.get_search(current_user_name, Word)
            self.send_message(T)

        elif current_command.endswith(" 사진"):
            print("{사진}", end="")
            Word = current_command[:-3]
            self.get_image(current_user_name, Word)

        elif current_command.endswith(" 번역"):
            print("{번역}", end="")
            word = current_command[:-3]
            self.get_translate(word)

        elif current_command.startswith("더보기"):
            print(" {사전:더보기} ", end="")
            Index = current_command[3:].strip()
            try:
                ind = int(Index)
                if ind in range(1, 4):
                    self.send_message(self.links[ind])
            except:
                pass

        elif current_command.endswith(" 책"):
            print(" {도서} ", end="")
            Book = current_command[:-2]
            self.get_book(current_user_name, Book)

        elif current_command.endswith(" 책들"):
            print(" {저자} ", end="")
            author = current_command[:-3]
            T = self.get_author(current_user_name, author)
            self.send_message(T)

        # elif current_command == "끝말잇기":
        #     print("{끝말잇기}", end="")
        #     if self.active_wordchain:
        #         print("{종료루틴}", end="")
        #         self.active_wordchain = False
        #         self.wordchain_last_user_answer = ""
        #         self.wordchain_last_bot_answer = ""
        #         self.wordchain_all_answers.clear()
        #         self.send_message("끝말잇기를 마칩니다 ^^")
        #     else:
        #         print("{시작루틴}", end="")
        #         self.active_wordchain = True
        #         self.send_message("끝말잇기를 시작할께요.\n3자로 된 명사를 먼저 시작하세요!")

        elif current_command.endswith("="):
            math = current_command[:-1]
            exp = math.strip()
            exp = exp.replace("÷", "/")
            exp = exp.replace("×", "*")
            exp = exp.replace("{", "(")
            exp = exp.replace("}", ")")
            result = re.compile(r"^([-+/*.\(\)\d])*").match(exp)
            g = result.group()
            eq = result.group() == exp
            if eq:
                answer = eval(exp)
                self.send_message("{}".format(answer))

        else:
            is_processed = False

        if is_processed:
            print("MESSAGE_PROCESSED")

        return

    def query_new_book(self, IsInit):
        """
            return text about new kyobo, howmistery book
        :return:
        """
        ret = ""
        # rv = self.get_kyobo_new_book()
        # if len(rv) != 0:
        #     if self.kyobo_title != rv[0]:
        #         text = "교보문고에 새 추리소설이 등록되었습니다.\n제목 : {}, 저자 : {}\n".format(rv[0], rv[1])
        #         self.kyobo_title = rv[0]
        #         self.kyobo_author = rv[1]
        #         ret = ret + text

        """
                rv = "" self.get_howmistery_new_book(IsInit)
                if len(rv) != 0:
                    if self.howmistery_title_author != rv:
                        text = "신간 소식이 있습니다.\n{}".format(rv)
                        self.howmistery_title_author = rv
                        ret = ret + text

                    driver.switch_to_window(driver.window_handles[1])
                    driver.find_element_by_xpath('//*[@id="content"]/section/div[3]/div/button').click()
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[2]/div').send_keys("여기에 글을 적습니다.\n여러가지")
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[3]/div/button').click()
                    driver.switch_to_window(driver.window_handles[0])

                """


        return ret

    def get_howmistery_new_book(self, IsInit = False):

        keywords = ""
        '''

        URL = "http://www.howmystery.com/newrelease"
        res = requests.get(URL)
        soup = BeautifulSoup(res.text, 'lxml')
        d = soup.find('li', {'class': 'notice'})
        s = d.findNext('li')
        s = s.find('p')
        s = s.find('b')

        if IsInit:
            with open('last_book.dic', 'wb') as f:
                pickle.dump(s.text, f)
            return ""

        new_books = [ s.text ]

        while True:
            if new_books[len(new_books)-1] == last_book:
                break

            s = s.findNext('li')
            s = s.find('p')
            s = s.find('b')
            delimeter = ":"
            if s.text.find(":") < 0:
                delimeter = ","
            pair = s.text.split(delimeter)
            if len(pair) == 1:
                new_books.append({"title": pair[0].strip(), "author": "없음"})
            else:
                new_books.append({"title":pair[0].strip(), "author":pair[1].strip()})

        # delete last book

        for index in range(len(new_books)-2, -1, -1): # range(5,-1,-1)
            book = new_books[index]

            keywords = "{} {}".format(book["title"], book["author"])

            ### 게시물 중지 ###

            url = "https://www.aladin.co.kr/m/msearch.aspx?SearchTarget=Book&KeyWord={}&KeyRecentPublish=0&OutStock=0&ViewType=Detail" \
                  "&SortOrder=5&CustReviewCount=0&CustReviewRank=0&KeyFullWord={}&KeyLastWord={}&CategorySearch=" \
                  "&MViewType=".format(keywords, keywords, keywords)
            r = requests.get(url)
            s = BeautifulSoup(r.text, 'lxml')
            div = s.find("div", { "class" : "browse_list_box" })
            anchors = div.findAll("a")
            if anchors[0]["href"].find("mproduct") > 0:
                try:
                    url = anchors[0]["href"]
                    r = requests.get(url)
                    s = BeautifulSoup(r.text, 'lxml')
                    image = s.find("img", { "class" : "coversize"})
                    image_url = image["src"]
                    image_url = "http:" + image_url

                    intro = s.find("div", {"id":"introduce_all"})
                    story = s.find("div", {"id":"Story_all"})
                    publisher = s.find("div", {"id":"Publisher_all"})

                    if intro is None:
                        p_intro = ""
                    else:
                        p_intro = intro.text

                    if story is None:
                        p_story = ""
                    else:
                        p_story = story.text

                    if publisher is None:
                        p_publisher = ""
                    else:
                        p_publisher = publisher.text

                    driver = self.getdriver()
                    driver.switch_to_window(driver.window_handles[1])
                    # begin write
                    driver.find_element_by_xpath('//*[@id="content"]/section/div[3]/div/button').click()
                    sleep(3)
                    # contents
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[2]/div').send_keys("\n")
                    sleep(1)
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[2]/div').send_keys("#신간\n")
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[2]/div').send_keys("{} - {}\n\n".format(book["title"], book["author"]))
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[2]/div').send_keys(p_intro+"\n\n")
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[2]/div').send_keys(p_story+"\n\n")
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[2]/div').send_keys(p_publisher+"\n\n")
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[2]/div').send_keys(image_url+"\n")
                    sleep(3)

                    # commit
                    driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[3]/div/button').click()
                    driver.switch_to_window(driver.window_handles[0])

                    with open('last_book.dic', 'wb') as f:
                        pickle.dump(book, f)

                except:
                    exc_type, exc_obj, tb = sys.exc_info()
                    f = tb.tb_frame
                    lineno = tb.tb_lineno
                    filename = f.f_code.co_filename
                    linecache.checkcache(filename)
                    line = linecache.getline(filename, lineno, f.f_globals)
                    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
                    print(traceback.print_exc())
                    continue
        '''
        return keywords

    def call_member(self, user):
        """
            call members
        :return:
        """
        driver = self.getdriver()
        if driver is None:
            return

        driver.find_element_by_xpath('//*[@id="write_comment_view1287"]').send_keys("@")
        sleep(0.5)
        driver.find_element_by_xpath('//*[@id="write_comment_view1287"]').send_keys(user)
        sleep(0.5)
        driver.find_element_by_xpath('//*[@id="write_comment_view1287"]').send_keys(Keys.ENTER)
        self.send_message("님!")

    def capture_screen(self):
        """
            capture browser screen
        :return:
        """
        driver = self.getdriver()
        if driver is None:
            return

        driver.save_screenshot("c:\\zextor\\screenshot.png")
        if pathlib.Path("c:\\zextor\\screenshot.png").is_file():
            f = driver.find_element_by_xpath('//*[@id="wrap"]/div[3]/div/div/div[1]/ul/li[2]/label/input')
            f.send_keys("c:\\zextor\\screenshot.png")

    def get_kyobo_new_book(self):
        URL = "http://www.kyobobook.co.kr/categoryRenewal/categoryMain.laf?linkClass=011504&mallGb=KOR&orderClick=JAR"
        res = requests.get(URL)
        soup = BeautifulSoup(res.text, 'lxml')
        detail = soup.findAll('div', {'class': 'detail'})
        for t in detail:
            title = t.find('div', {'class': 'title'})
            title_text = title.find('strong').text
            author = t.find('div', {'class': 'pub_info'})
            author_text = author.find('span', {'class': 'author'}).text

            rv = []
            rv.append(title_text)
            rv.append(author_text)
            return rv
        return None

    def alert(self, value):
        """
            미세먼지 알람
        :return:
        """
        v = int(value)
        if  v > 151:
            return "매우나쁨"
        if v > 80:
            return "나쁨"
        if v > 30:
            return "보통"
        return "좋음"

    def query_weather(self):
        """
            return text about weather
        :return:
        """
        l = self.get_weather_from_naver();
        r = "현재 날씨 입니다.\n"


        r += "서울:{}{}°C,미세먼지 {}({})\n".format(l["서울"][1]['구름'],l["서울"][0]['온도'], self.alert(l["서울"][2]["미세먼지"]),l["서울"][2]["미세먼지"])
        r += "경기:{}{}°C,미세먼지 {}({})\n".format(l["수원"][1]['구름'], l["수원"][0]['온도'], self.alert(l["수원"][2]["미세먼지"]), l["수원"][2]["미세먼지"])
        r += "강원:{}{}°C,미세먼지 {}({})\n".format(l["춘천"][1]['구름'], l["춘천"][0]['온도'], self.alert(l["춘천"][2]["미세먼지"]), l["춘천"][2]["미세먼지"])
        r += "대구:{}{}°C,미세먼지 {}({})\n".format(l["대구"][1]['구름'], l["대구"][0]['온도'], self.alert(l["대구"][2]["미세먼지"]), l["대구"][2]["미세먼지"])
        r += "광주:{}{}°C,미세먼지 {}({})\n".format(l["목포"][1]['구름'], l["목포"][0]['온도'], self.alert(l["목포"][2]["미세먼지"]), l["목포"][2]["미세먼지"])
        r += "부산:{}{}°C,미세먼지 {}({})\n".format(l["부산"][1]['구름'], l["부산"][0]['온도'], self.alert(l["부산"][2]["미세먼지"]), l["부산"][2]["미세먼지"])

        return r

    @property
    def get_keywords(self):
        """
            network for keywords
        :return:

        res = requests.get("https://www.naver.com")
        s = BeautifulSoup(res.text, 'lxml')
        ul = s.find('div', {'class': 'PM_CL_realtimeKeyword_rolling'})

        if len(ul) == 0:
            return None

        li_tag = ul.findAll('span', {'class': 'ah_k'})
        if len(li_tag) == 0:
            return None

        self.rank = self.rank_format.format(li_tag[0].text, li_tag[1].text, li_tag[2].text)

        rv = set()
        for item in li_tag:
            rv.add(item.text)

        return rv
        """
        pass

    def query_keywords(self):
        """
            return text about naver rasing keywords
        :return: text

        rv = self.get_keywords
        if len(rv) != 0:
            diff = rv - self.keywords_before
            self.keywords_before = diff
            text = "현재 급상승 인기검색어는 '{}'입니다.\n{}".format(", ".join(diff), self.rank)
            return text
        else:
            return ""
        """
        pass


    def get_weather_from_naver(self):
        """
            get weather from naver
        :return:
        """
        URL = "http://m.search.naver.com/search.naver?query=전국날씨&where=m&sm=mtp_sug.top&qdt=0&acq=전국날씨&acr=1"
        res = requests.get(URL, headers=HEADERS_FOR_NAVER)
        soup = BeautifulSoup(res.text, 'lxml')

        ptr =  soup.find('span', { 'class' : 'lcl_name' } )
        target  = ["서울", "수원", "대구", "목포", "부산", "춘천"]
        target1 = ["서울", "경기", "대구", "광주", "부산", "강원"]
        city = ""
        result_new = dict()
        while True:
            is_include_city = False
            if not ptr: # 도시
                break
            print("{} ".format(ptr.text))
            if ptr.text in target:
                is_include_city = True
                city = ptr.text
            else:
                is_include_city = False

            ptr = ptr.findNext('span')      # 온도
            if is_include_city:
                temp = { "온도" :  ptr.contents[0] }

            ptr = ptr.findNext('span', { 'class' : 'ico_status2'})
            if is_include_city:
                cloud = { "구름" : ptr.text }
                result_new[city] = [ temp, cloud ]

            ptr = ptr.findNext('span', { 'class' : 'lcl_name' })

        print("\n미세먼지\n")


        URL_dirsty = "https://m.search.naver.com/search.naver?query=전국+미세먼지&sm=mtb_hty.top&where=m&oquery=미세먼지&tqi=UvwkUlpVuq8ssbfb9f8ssssstVZ-333588"
        res_d = requests.get(URL_dirsty, headers=HEADERS_FOR_NAVER)
        soup_d = BeautifulSoup(res_d.text, 'lxml')
        ptr = soup_d.find('span', {'class': 'lcl_name'})

        """
            경기>수원 광주>목포 강원>춘천 에 넣어야 함
            
        """
        while True:
            is_in = False

            if not ptr:
                break

            if ptr.text in target1:
                is_in = True
                if ptr.text == "경기":
                    city = "수원"
                elif ptr.text == "광주":
                    city = "목포"
                elif ptr.text == "강원":
                    city = "춘천"
                else:
                    city = ptr.text

            ptr = ptr.findNext('span') #미세먼지
            if is_in:
                result_new[city].append( { "미세먼지": ptr.text } )
                if city == "목포":
                    break

            ptr = ptr.findNext('span', {'class': 'lcl_name'})

        return result_new

    def download_image(self,img_url):
        r = requests.get(img_url)
        if r.status_code != 200:
            return False

        localfile = "c:\\zextor\\download_image.jpg"
        if len(r.content) < 1024:  # 404 일 경우 취소함
            return False

        with open(localfile, "wb") as code:
            code.write(r.content)

        f = self.driver.find_element_by_xpath('//*[@id="wrap"]/div[3]/div/div/div[1]/ul/li[2]/label/input')
        f.send_keys(localfile)
        return True


    def get_book(self, User, Query):

        ptr = Query.find(",")
        if ptr >= 0:
            title = Query[:ptr].strip()
            author = Query[ptr+1:].strip()
            URL = "https://openapi.naver.com/v1/search/book_adv.xml?display=1&start=1&d_titl=" + title+ "&d_auth=" + author
        else:
            URL = "https://openapi.naver.com/v1/search/book_adv.xml?display=1&start=1&d_titl=" + Query

        res = requests.get(URL, headers=HEADERS_NAVER_OPENAPI)
        s = BeautifulSoup(res.text, 'lxml')
        p = s.find('item')
        if p:
            title = get_pure_text(p.findNext('title').text)
            pos = p.findNext('image').text.find('?')
            if pos > 0:
                image = p.findNext('image').text[:pos]
            else:
                image = p.findNext('image').text
            author = get_pure_text(p.findNext('author').text)
            Price = get_pure_text(p.findNext('price').text)
            if len(Price) < 1:
                Price = "0"
            desc = get_pure_text(p.findNext('description').text)
            ret = "{}님 {} 검색결과입니다.\n{} - {}\n가격 {:,}원\n{}".format(User, Query, title, author, int(Price), desc)
            self.send_message(ret)
            self.download_image(image)
            return
        else:
            self.send_message("{}님 검색결과가 없습니다.".format(User))
        return


    def get_author(self, User, author):
        """
            get book list writed by author
        :param User:
        :param Author:
        :return: result text
        """
        URL = "https://openapi.naver.com/v1/search/book_adv.xml?display=15&start=1&d_auth=" + author
        res = requests.get(URL, headers=HEADERS_NAVER_OPENAPI)
        if res.status_code == 200:
            ret = ""
            s = BeautifulSoup(res.text, 'lxml')
            total_count = s.find("total").text
            ret += "총 {}권이 검색되었습니다.\n".format(total_count)
            titles = s.findAll("title") # 여기는 결과제목 1개가 더 포함되어 있음
            authors = s.findAll("author")
            publisher = s.findAll("publisher")
            pubdate = s.findAll("pubdate")
            for i in range(0, min(15, int(total_count))):
                ret += "{}. {} - {} ({} {})\n".format(i+1
                                                      , get_pure_text(titles[i+1].text)
                                                      , get_pure_text(authors[i].text)
                                                      , get_pure_text(pubdate[i].text)[:4]
                                                      , get_pure_text(publisher[i].text))
            if int(total_count) > 15:
                ret += "결과가 많아 이후는 생략합니다.\n"

        else:
            return "CODE {} 발생".format(res.status_code)

        return ret

    def get_translate(self, sentence):
        self.driver.switch_to.window(self.driver.window_handles[2])
        self.driver.get("https://translate.google.co.kr/#view=home&op=translate&sl=auto&tl=ko&text={}".format(sentence))
        time.sleep(1)
        s = BeautifulSoup(self.driver.page_source, 'lxml')
        t1 = s.find('span', {'class': 'tlid-translation translation'})
        self.driver.switch_to.window(self.driver.window_handles[0])
        time.sleep(1)
        if len(t1) > 0:
            self.send_message("변역 결과: {}".format(t1.text))

        return

    def get_image(self, User, Word):
        """
            사진검색, 브라우저 3번째 탭이 사용가능해야 함
        :param User:
        :param Word:
        :return:
        """

        self.driver.switch_to.window(self.driver.window_handles[2])
        self.driver.get("https://www.google.com/search?as_st=y&tbm=isch&hl=ko&safe=active&tbs=isz:l&as_q="+Word)

        for index in range(1, 4):
            try:
                self.driver.switch_to.window(self.driver.window_handles[2])
                xpath = '//*[@id="rg_s"]/div[{}]/a[1]'.format(index)
                we = self.driver.find_element_by_xpath(xpath)
                u = we.get_attribute("href")
                parsed = urlparse(u)
                img = parse_qs(parsed.query)["imgurl"]
                img_url = img[0]
                img_url = img_url.replace("https", "http")
                r = requests.get(img_url)
                if r.status_code != 200:
                    continue

                localfile ="c:\\zextor\\download_image_{}.jpg".format(index)
                if len(r.content) < 1024:       # 404 일 경우 취소함
                    continue

                with open(localfile, "wb") as code:
                    code.write(r.content)

                self.driver.switch_to_window(self.driver.window_handles[0])
                f = self.driver.find_element_by_xpath('//*[@id="wrap"]/div[3]/div/div/div[1]/ul/li[2]/label/input')
                f.send_keys(localfile)
                # 파일 전송시 에러가 나면 alert이 뜰 때까지 시간이 소요된다
                # 따라서 그 전에 switch_to_alert 를 호출하면 예외가 발생하므로
                # 충분한 시간을 가지고 대기한 후 alert를 확인해야 함
                sleep(5)
                alert = self.driver.switch_to_alert()
                # 여기온건 Alert 창이 있다는 뜻
                alert.accept()

            except Exception as e:
                print("no alert")
                continue

        sleep(1)
        self.driver.switch_to_window(self.driver.window_handles[0])
        return

    def get_search(self, User, Word):
        """
            키워드 검색
        :param User:
        :param Word:
        :return:
        """
        URL = "https://openapi.naver.com/v1/search/encyc.json?query=" + Word
        res = requests.get(URL, headers=HEADERS_NAVER_OPENAPI)
        data = json.loads(res.text)

        if data['display'] > 0:
            Means = "{}님 {}의 검색결과 입니다.".format(User, Word)
            Index = 1
            for item in data['items']:
                Text = item['description']
                R = get_pure_text(Text)
                R2 = "{}. {}".format(Index, R)
                Means = Means + "\n" + R2
                if len(item['link']) > 0:
                    self.links[Index] = item['link']
                Index = Index + 1
                if Index == 4:
                    break
            return Means
        else:
            return "{}님 검색결과가 없습니다.".format(User)

    def get_dic(self, User, Word):
        """
            사전적 의미
        :param User:
        :param Word:
        :return:
        """
        url = "https://ko.dict.naver.com/api3/koko/search?query={}&m=pc&hid=154702086874655600&range=word&page=1".format(Word)

        r = requests.get(url)
        j = json.loads(r.text)

        result = "{}님 '{}'의 사전 내용입니다.\n".format(User, Word)

        found = False
        index = 1
        for item in j["searchResultMap"]["searchResultListMap"]["WORD"]["items"]:

            a = get_pure_text(item["handleEntry"])
            b = get_pure_text(Word)
            if a.replace(" ", "") == b.replace(" ", ""):
                for mean in item["meansCollector"]:
                    result += "{}.{} ({})\n".format(index, mean["partOfSpeech"], item["sourceDictnameKO"])

                    for value in mean["means"]:
                        result += " - {}\n".format(get_pure_text(value["value"]))

                    found = True

            index = index + 1

        if found:
            return result

        return "{}님 '{}'는 사전에 없습니다.".format(User, Word)

    def get_tv_rating(self):
        """
            tv rating
        :return: llist
        """
        url = [ "https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=1_2&area=00",
                "https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=2_2&area=00",
                "https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp?menu=Tit_1&sub_menu=3_2&area=00"]
        list = []
        for u in url:
            r = requests.get(u)
            s = BeautifulSoup(r.content, 'lxml')
            ptr = s.find('tr', {'class':'ranking_title'})
            index = 1
            while ptr :
                ptr = ptr.findNextSibling()
                td = ptr.findNext('td') # rank
                td = td.findNext('td') # company
                channel = td.text.strip()
                td = td.findNext('td')
                title = td.text.strip()
                td = td.findNext('td')
                percent = float(td.text.strip())
                list.append(tuple((percent, title, channel)))
                index = index + 1
                if index > 10:
                    break
        list.sort(reverse=True)
        return list

    def query_tv_rating(self):
        """
            show formated result tv show
        :return: text
        """
        l = self.get_tv_rating()
        T = ""
        index = 1
        for i in l:
            text = "{}. {:.1f}% {} {}\n".format(index, i[0], i[1], i[2])
            T = T + text
            index = index + 1
            if index > 15:
                break

        return T

    def is_word(self, word):
        """
            정말 단어인가
        :param word:
        :return:
        """
        url = "https://ko.dict.naver.com/api3/koko/search?query=" + word + "&m=pc&hid=154702086874655600&range=word&page=1"
        r = requests.get(url)
        j = json.loads(r.text)

        if len(j["searchResultMap"]["searchResultListMap"]["WORD"]["items"]) == 0:
            return False

        for item in j["searchResultMap"]["searchResultListMap"]["WORD"]["items"]:
            a = get_pure_text(item["handleEntry"])
            b = get_pure_text(word)
            if a.replace(" ", "") == b.replace(" ", ""):
                return True

        return False

    def wordchain(self, word):
        """
            끝말잇기
        :param word:
        :return:
        """
        ret = []
        ret_answer = ""
        try_num = 1
        T = "{}??".format(word[2])

        while True:
            url = "https://ko.dict.naver.com/api3/koko/search?query={}&m=pc&hid=154702086874655600&range=word&page={}".format(T, try_num)

            r = requests.get(url)
            j = json.loads(r.text)

            for item in j["searchResultMap"]["searchResultListMap"]["WORD"]["items"]:
                if item["meansCollector"][0]["partOfSpeech"] == "명사":
                    if len(item["handleEntry"]) == 3:
                        ret.append(tuple((item["priority"], item["handleEntry"])))

            if len(ret) == 0:
                try_num = try_num + 1
            else:
                break

            if try_num == 4:
                return ""

        for item in ret:
            if item[1] in self.wordchain_all_answers:
                continue
            else:
                ret_answer = item[1]
                if ret_answer[0] == word[2]:
                    break
                else:
                    continue

        if len(ret_answer) == 0:
            return ""

        return ret_answer



