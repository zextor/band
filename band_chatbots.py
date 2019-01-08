from bs4 import BeautifulSoup
import requests
import json
import lxml
import re
import html
import pprint


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
        self.callback = None
        self.keywords_before = set("empty_set")
        self.rank_format = "\n1위: {}\n2위: {}\n3위: {}"
        self.rank = ""
        self.kyobo_title = ""
        self.kyobo_author = ""
        self.howmistery_title_author = ""
        self.BeforeCmd = ""
        self.BeforeUser = ""
        self.links = { 1: "등록안됨", 2: "등록안됨", 3: "등록안됨"}

        # drop first value
        temp = self.query_keywords()
        temp = self.query_new_book()

    def __str__(self):
        return "This is ChatBot class : {}".format(self.init)

    def register_callback(self, func):
        """
            register callback function
        :func       function for call back
        :return:
        """
        self.callback = func

    def query(self, text):
        """
            process chat
        :param text:
        :return: text
        """
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

        if CurrentCmd == "날씨":
            print(" {날씨} ", end="")
            ret = "{} 님 현재날씨입니다.\n{}".format(CurrentUser, self.query_weather())
            self.callback(ret)

        elif CurrentCmd == "뽀봇":
            print(" {핑퐁} ", end="")
            self.callback("네! " + CurrentUser + "님")

        elif CurrentCmd in ["시청률", "시청율", "드라마", "예능"]:
            print(" {시청률}", end="")
            l = self.query_tv_rating()
            self.callback(CurrentUser+"님 실시간 시청율입니다.")
            self.callback(l)

        elif CurrentCmd.endswith(" 뜻"):
            print(" {사전} ", end="")
            Word = CurrentCmd[:-2]
            T = self.get_dic(CurrentUser, Word)
            self.callback(T)

        elif CurrentCmd.startswith("더보기"):
            print(" {사전:더보기} ", end="")
            Index = CurrentCmd[3:].strip()
            try:
                ind = int(Index)
                if ind in range(1, 4):
                    self.callback(self.links[ind])
            except:
                pass


        elif CurrentCmd.endswith(" 책"):
            print(" {도서} ", end="")
            Book = CurrentCmd[:-2]
            T = self.get_book(CurrentUser, Book)
            self.callback(T)

        else:
            isProcessed = False
            print("Bypass")

        if isProcessed:
            print("Processed")

        return ""


    def query_new_book(self):
        """
            return text about new kyobo, howmistery book
        :return:
        """
        ret = ""
        rv = self.get_kyobo_new_book()
        if len(rv) != 0:
            if self.kyobo_title != rv[0]:
                text = "교보문고에 새 추리소설이 등록되었습니다.\n제목 : {}, 저자 : {}\n".format(rv[0], rv[1])
                self.kyobo_title = rv[0]
                self.kyobo_author = rv[1]
                ret = ret + text

        rv = self.get_howmistery_new_book()
        if len(rv) != 0:
            if self.howmistery_title_author != rv:
                text = "하우미스터리에 새 추리소설이 등록되었습니다.\n{}".format(rv)
                self.howmistery_title_author = rv
                ret = ret + text

        return ret

    def get_howmistery_new_book(self):
        URL = "http://www.howmystery.com/newrelease"
        res = requests.get(URL)
        soup = BeautifulSoup(res.text, 'lxml')
        d = soup.find('li', {'class': 'notice'})
        s = d.findNext('li')
        s = s.find('p')
        s = s.find('b')
        text = s.text
        return text

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

    def query_weather(self):
        """
            return text about weather
        :return:
        """
        l = self.get_weather_from_naver();
        r = ""
        while l:
            T = "{2} {1} {0}".format(l.pop(), l.pop(), l.pop())
            if len(r) == 0:
                r = T
            else:
                r = r + "\n" + T
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
        result = []
        target = [ "서울", "대구", "목포", "부산", "춘천"]
        while True:
            isIn = False
            if not ptr:                     # 도시
                break

            if ptr.text in target:
                isIn = True
                result.append(ptr.text)
            else:
                isIn = False

            ptr = ptr.findNext('span')      # 온도
            if isIn:
                result.append(ptr.text)
            ptr = ptr.findNext('span', { 'class' : 'ico_status2'})
            if isIn:
                result.append(ptr.text)
            ptr = ptr.findNext('span', { 'class' : 'lcl_name' })
        return result

    def get_book(self, User, Query):

        ptr = Query.find(",")
        if ptr > 0:
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


    def get_dic(self, User, Word):

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
        return "{}님 검색결과가 없습니다.".format(User)

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


