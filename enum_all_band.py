from bs4 import BeautifulSoup
import requests
import json
from time import sleep
import codecs

def is_live(index):
    """
        band 가 존재하는지 확인
    :param index:
    :return:
    """
    HEADERS_FOR_NAVER = {
    "Host": "api.band.us",
    "Connection": "keep-alive",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Origin": "https://band.us",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Referer": "https://band.us/band/73188261",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cookie": 'di=web-AAAAAAMFT3q0nDC8RO3AWcFOttKMJbQ-hAhKLg9eAZl_KEMAPq7W-SGW73_c8CaRNGy7lA; _ga=GA1.2.754575919.1546409176; language=ko; BBC=49Du7bRwQiRaLKdsTDXrOv; _gid=GA1.2.1417865134.1547425659; band_session=ZQIAAGERN8JGjhXjG4Gx0-iQZNaftfxs-klo88ZK8Ga4KWFKbT-hfOccFKwasScj2OBMqJaovs2mPvaTAWEuUt70Ngmi1tIBOPu76DHFOIloPfK8; as="6c2f8278:o1MhWQr/OfExYGytX3zb1NI8EVlvWwfrgigBc+sbD6A="; ai="1ddecc9,1686888ef88"; band_center_session="6Ud7lM9aEQNIP6dwH6+ebJU0STeFCR1q5YKvxCMFBY8="; _gat_UA-57714604-1=1'
    }

    url = "https://api.band.us/v2.0.0/get_band_information?client_info=%7B%22language%22%3A%22ko%22%2C%22country%22%3A%22KR%22%2C%22version%22%3A1%2C%22agent_type%22%3A%22web%22%2C%22agent_version%22%3A%223.3.1%22%2C%22resolution_type%22%3A4%7D&language=ko&country=KR&version=1&akey=bbc59b0b5f7a1c6efe950f6236ccda35&DEVICE-TIME-ZONE-ID=Asia%2FSeoul&DEVICE-TIME-ZONE-MS-OFFSET=32400000&md=xvhaLN3NQAcf46hqRN5mh0AQJ4s4mxj1fWPTNF8VvlQ%3D&ts=1547796628111&band_no={}&_=1547796627154".format(index)
    res = requests.get(url, headers = HEADERS_FOR_NAVER)
    data = json.loads(res.text)
    if data["result_code"] == 1:
        r = "{}|{}|{}|{}\n".format(index,data["result_data"]["band"]["member_count"],data["result_data"]["band"]["name"],data["result_data"]["band"]["keywords"])
        return r
    else:
        print("{} {} - {}".format(index, data["result_code"], data["result_data"]["message"]))
    return ""



if __name__ == '__main__':

    file = codecs.open("band_list.txt", "w", "utf-8")
    for index in range(73188261, -1, -1):
        r = is_live(index)
        if len(r) > 0:
            file.write(r)
            print(r)

        sleep(1)
    file.close()

