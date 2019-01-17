import re
import sys
import html
import json
import lxml
import pprint
import pickle
import pathlib
import requests
import traceback
import linecache
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

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


class ChatBot(object):
    """
        class for chat service
    """

    def __init__(self):
        """
            for init class
        """
        self.init = True
        self.sendmessage = None
        self.refresh = None
        self.getdriver = None
        self.keywords_before = set("empty_set")
        self.rank_format = "\n1위: {}\n2위: {}\n3위: {}"
        self.rank = ""
        self.kyobo_title = ""
        self.kyobo_author = ""
        self.howmistery_title_author = ""
        self.BeforeCmd = ""
        self.BeforeUser = ""
        self.links = { 1: "등록안됨", 2: "등록안됨", 3: "등록안됨"}
        self.active_wordchain = False
        self.wordchain_all_answers = []
        self.wordchain_last_user_answer = ""
        self.wordchain_last_bot_answer = ""

        # drop first value
        temp = self.query_keywords()
        # temp = self.query_new_book(None)

    def __str__(self):
        return "This is ChatBot class : {}".format(self.init)

    def register_callback_getdriver(self, func):
        """
            register get driver
        :param func:
        :return:
        """
        self.getdriver = func

    def register_callback_refresh(self, func):
        """
            register refresh function
        :param func:
        :return:
        """
        self.refresh = func

    def register_callback_sendmessage(self, func):
        """
            register callback function
        :func       function for call back
        :return:
        """
        self.sendmessage = func

    def query(self, text):
        """
            process chat
        :param text:
        :return: text
        """
        try:
            pos1 = text.find(':')
            pos2 = text.find(':', pos1 + 1)
            CurrentUser = text[pos1 + 2:pos2 - 1]
            CurrentCmd = text[pos2 + 2:]

            # 같은 메세지이면 패스
            if self.BeforeCmd == CurrentCmd and self.BeforeUser == CurrentUser:
                return ""

            self.BeforeUser = CurrentUser
            self.BeforeCmd = CurrentCmd

            print("명령 : {}".format(text))

            isProcessed = True

            if self.active_wordchain:
                token = get_pure_text(CurrentCmd)
                if len(token) == 3:
                    if len(self.wordchain_last_bot_answer) != 0:                # 이전답의 잇기가 아니면
                        if self.wordchain_last_bot_answer[2] != token[0]:
                            return "'{}' 끝말을 이어주세요.".format(self.wordchain_last_bot_answer[2])

                    if not self.is_word(token):
                        return "'{}' 는 사전에 없는 명사네요.".format(token)

                    if token in self.wordchain_all_answers:
                        return "'{}' 은/는 이미 사용한 명사에요!".format(token)

                    T = self.wordchain(token)
                    if len(T) == 0:
                        T = "제가 졌네요ㅠㅠ\n{}님이 이겼어요!".format(CurrentUser)
                        self.active_wordchain = False
                        self.wordchain_last_user_answer = ""
                        self.wordchain_last_bot_answer = ""
                        self.wordchain_all_answers.clear()
                    else:
                        self.wordchain_last_user_answer = token
                        self.wordchain_last_bot_answer = T
                        self.wordchain_all_answers.append(token)
                        self.wordchain_all_answers.append(T)
                    return T

            if CurrentCmd == "날씨":
                print("{날씨}", end="")
                ret = "{} 님 현재날씨입니다.\n{}".format(CurrentUser, self.query_weather())
                self.sendmessage(ret)

            elif CurrentCmd == "캡쳐":
                print("{캡쳐}", end="")
                self.capture_screen()

            elif CurrentCmd == "뽀봇":
                print("{핑퐁}", end="")
                self.sendmessage("네! " + CurrentUser + "님")

            elif CurrentCmd == "빨리":
                print("{브라우저갱신}", end="")
                self.sendmessage("{}님! 더 빨리 대답할께요ㅠ".format(CurrentUser))
                self.refresh()

            elif CurrentCmd in ["시청률", "시청율", "드라마", "예능"]:
                print("{시청률}", end="")
                l = self.query_tv_rating()
                self.sendmessage(CurrentUser + "님 실시간 시청율입니다.")
                self.sendmessage(l)

            elif CurrentCmd.endswith(" 뜻"):
                print("{사전}", end="")
                Word = CurrentCmd[:-2]
                T = self.get_dic(CurrentUser, Word)
                self.sendmessage(T)

            elif CurrentCmd.endswith(" 검색"):
                print("{검색}", end="")
                Word = CurrentCmd[:-3]
                T = self.get_search(CurrentUser, Word)
                self.sendmessage(T)

            elif CurrentCmd.endswith(" 사진"):
                print("{사진}", end="")
                Word = CurrentCmd[:-3]
                self.get_image(CurrentUser, Word)

            elif CurrentCmd.startswith("더보기"):
                print(" {사전:더보기} ", end="")
                Index = CurrentCmd[3:].strip()
                try:
                    ind = int(Index)
                    if ind in range(1, 4):
                        self.sendmessage(self.links[ind])
                except:
                    pass

            elif CurrentCmd.endswith(" 책"):
                print(" {도서} ", end="")
                Book = CurrentCmd[:-2]
                T = self.get_book(CurrentUser, Book)
                self.sendmessage(T)

            elif CurrentCmd.endswith(" 책들"):
                print(" {저자} ", end="")
                author = CurrentCmd[:-3]
                T = self.get_author(CurrentUser, author)
                self.sendmessage(T)

            elif CurrentCmd == "끝말잇기":
                print("{끝말잇기}", end="")
                if self.active_wordchain:
                    print("{종료루틴}", end="")
                    self.active_wordchain = False
                    self.wordchain_last_user_answer = ""
                    self.wordchain_last_bot_answer = ""
                    self.wordchain_all_answers.clear()
                    self.sendmessage("끝말잇기를 마칩니다 ^^")
                else:
                    print("{시작루틴}", end="")
                    self.active_wordchain = True
                    self.sendmessage("끝말잇기를 시작할께요.\n3자로 된 명사를 먼저 시작하세요!")

            elif CurrentCmd.endswith("="):
                math = CurrentCmd[:-1]
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
                    return "{}".format(answer)

            else:
                isProcessed = False
                print("{Bypass}")

            if isProcessed:
                print("{Processed}")

            return ""
        except:
            exc_type, exc_obj, tb = sys.exc_info()
            f = tb.tb_frame
            lineno = tb.tb_lineno
            filename = f.f_code.co_filename
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
            print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
            print(traceback.print_exc())

    def query_new_book(self, driver):
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

        rv = self.get_howmistery_new_book()
        if len(rv) != 0:
            if self.howmistery_title_author != rv:
                text = "신간 소식이 있습니다.\n{}".format(rv)
                self.howmistery_title_author = rv
                ret = ret + text


        """
            driver.switch_to_window(driver.window_handles[1])
            driver.find_element_by_xpath('//*[@id="content"]/section/div[3]/div/button').click()
            driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[2]/div').send_keys("여기에 글을 적습니다.\n여러가지")
            driver.find_element_by_xpath('//*[@id="wrap"]/div[2]/div/div/section/div/div/div/div[3]/div/button').click()
            driver.switch_to_window(driver.window_handles[0])

        """
        return ret

    def get_howmistery_new_book(self):

        keywords = ""

        with open('last_book.dic', 'rb') as f:
            last_book = pickle.load(f)

        URL = "http://www.howmystery.com/newrelease"
        res = requests.get(URL)
        soup = BeautifulSoup(res.text, 'lxml')
        d = soup.find('li', {'class': 'notice'})
        s = d.findNext('li')
        s = s.find('p')
        s = s.find('b')
        delimeter = ":"
        if s.text.find(":") < 0:
            delimeter = ","
        pair = s.text.split(delimeter)
        new_books = [{"title":pair[0].strip(), "author":pair[1].strip()}]

        while True:
            if new_books[len(new_books)-1]["title"] == last_book["title"]:
                break

            s = s.findNext('li')
            s = s.find('p')
            s = s.find('b')
            delimeter = ":"
            if s.text.find(":") < 0:
                delimeter = ","
            pair = s.text.split(delimeter)
            new_books.append({"title":pair[0].strip(), "author":pair[1].strip()})

        # delete last book

        for index in range(len(new_books)-2, -1, -1): # range(5,-1,-1)
            book = new_books[index]

            keywords = "{} {}".format(book["title"], book["author"])

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

        return keywords


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


        r += "서울:{}({}°C),미세먼지 {}({})\n".format(l["서울"][1]['구름'],l["서울"][0]['온도'], self.alert(l["서울"][2]["미세먼지"]),l["서울"][2]["미세먼지"])
        r += "경기/수원:{}({}°C),미세먼지 {}({})\n".format(l["수원"][1]['구름'], l["수원"][0]['온도'], self.alert(l["수원"][2]["미세먼지"]), l["수원"][2]["미세먼지"])
        r += "강원/춘천:{} {}°C,미세먼지 {}({})\n".format(l["춘천"][1]['구름'], l["춘천"][0]['온도'], self.alert(l["춘천"][2]["미세먼지"]), l["춘천"][2]["미세먼지"])
        r += "대구:{} {}°C,미세먼지 {}({})\n".format(l["대구"][1]['구름'], l["대구"][0]['온도'], self.alert(l["대구"][2]["미세먼지"]), l["대구"][2]["미세먼지"])
        r += "광주/목포:{} {}°C,미세먼지 {}({})\n".format(l["목포"][1]['구름'], l["목포"][0]['온도'], self.alert(l["목포"][2]["미세먼지"]), l["목포"][2]["미세먼지"])
        r += "부산:{} {}°C,미세먼지 {}({})\n".format(l["부산"][1]['구름'], l["부산"][0]['온도'], self.alert(l["부산"][2]["미세먼지"]), l["부산"][2]["미세먼지"])

        return r

    @property
    def get_keywords(self):
        """
            network for keywords
        :return:
        """
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

    def query_keywords(self):
        """
            return text about naver rasing keywords
        :return: text
        """
        rv = self.get_keywords
        if len(rv) != 0:
            diff = rv - self.keywords_before
            self.keywords_before = diff
            text = "현재 급상승 인기검색어는 '{}'입니다.\n{}".format(", ".join(diff), self.rank)
            return text
        else:
            return ""

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
            author = get_pure_text(p.findNext('author').text)
            Price = get_pure_text(p.findNext('price').text)
            desc = get_pure_text(p.findNext('description').text)
            ret = "{}님 {} 검색결과입니다.\n{} - {}\n가격 {}원\n{}".format(User, Query, title, author, Price, desc)
            return ret
        return "{}님 검색결과가 없습니다.".format(User)

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
            for i in range(0, min(15, int(total_count))):
                ret += "{}. {} - {}\n".format(i+1, get_pure_text(titles[i+1].text), get_pure_text(authors[i].text))
            if int(total_count) > 15:
                ret += "결과가 많아 이후는 생략합니다.\n"

        else:
            return "CODE {} 발생".format(res.status_code)

        return ret

    def get_image(self, User, Word):
        """
            사진검색, 브라우저 3번째 탭이 사용가능해야 함
        :param User:
        :param Word:
        :return:
        """
        driver = self.getdriver()
        if driver is None:
            return

        driver.switch_to.window(driver.window_handles[2])
        sleep(0.5)
        driver.get("https://www.google.com/search?as_st=y&tbm=isch&hl=ko&safe=active&tbs=isz:l&as_q="+Word)

        for index in range(1,4):
            try:
                driver.switch_to.window(driver.window_handles[2])

                xpath = '//*[@id="rg_s"]/div[{}]/a[1]'.format(index)
                we = driver.find_element_by_xpath(xpath)
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

                driver.switch_to_window(driver.window_handles[0])
                sleep(0.5)

                f = driver.find_element_by_xpath('//*[@id="wrap"]/div[3]/div/div/div[1]/ul/li[2]/label/input')
                f.send_keys(localfile)
                alert = driver.switch_to_alert()
                if alert is None:
                    print("No Alert")
                else:
                    alert.accept()
                    print("Alert Accept")
            except Exception as e:
                sleep(0.1)
                print("no alert")
                continue

        driver.switch_to_window(driver.window_handles[0])
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



