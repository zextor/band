import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def get_yes24_point(title):
    url = "http://www.yes24.com/searchcorner/Search?keywordAd=&keyword=&qdomain=%c0%fc%c3%bc&Wcode=001_0050&" \
            "query={}&domain=BOOK&" \
            "scode=006_002".format(quote(title.encode('euc-kr')))

    point = "0"

    try:
        r = requests.get(url)
        s = BeautifulSoup(r.text, 'lxml')
        div = s.find('div',{'class':'goodsList'})
        book_url = 'http://www.yes24.com/' + div.find('a')['href']
        sr = requests.get(book_url)
        ss = BeautifulSoup(sr.text, 'lxml')
        point = ss.find('em',{'class':'yes_b'}).text
        if point.find(',') > 0:
            point = '0'

    except:
        pass

    return point

def get_aladin_point(title):
    url = "https://www.aladin.co.kr/m/msearch.aspx?SearchTarget=Book&KeyWord={}&KeyRecentPublish=0&OutStock=0&ViewType=Detail" \
    "&SortOrder=5&CustReviewCount=0&CustReviewRank=0&KeyFullWord={}&KeyLastWord={}&CategorySearch=" \
    "&MViewType=".format(title, title, title)

    point = "0"

    try:
        r = requests.get(url)
        s = BeautifulSoup(r.text, 'lxml')
        anchor = s.find("div", {"class": "browse_list_box"}).find('a')
        if anchor["href"].find("mproduct") > 0:
            book_url = anchor["href"]
            sr = requests.get(book_url)
            ss = BeautifulSoup(sr.text, 'lxml')
            point = ss.find('li',{'class':'star_num'}).text
    except:
        pass

    return point

def get_new_book():
    r = requests.get("http://www.howmystery.com/index.php?mid=newrelease&listStyle=list")
    s = BeautifulSoup(r.text, 'lxml')
    items = s.findAll('tr')
    book_list = []
    for item in items:
        title = ""
        try :
            title = item.find('td',{'class':'title'}).find('a').text.replace('\n','').replace('\t','')
        except:
            continue
        if title == "이곳은 '새책소식'입니다.":
            continue
        book_list.append(title)
    return book_list

if __name__ == '__main__':

    book_list = get_new_book()
    for book in book_list:
        aladin_point = get_aladin_point(book.replace(',',' '))
        yes24_point = get_yes24_point(book.replace(',',' '))
        print("|{}|{}|{}|".format(aladin_point, yes24_point, book))