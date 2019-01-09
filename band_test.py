import band_chatbots
import pathlib
from os import rename

def cb(text):
    print(text)


# try:
#     if pathlib.Path("update.now").is_file():
#         rename("update.now", "update.complete(change .now for reload)")
#         print("module chatbot reload completed.")
#
# except Exception:
#     pass


c = band_chatbots.ChatBot()
c.register_callback(cb)

c.query_weather()
c.query_keywords()
c.query_new_book()
c.query_tv_rating()

# test

c.query("새로운 메세지 : 란뽀 : 김유란 책들")
c.query("새로운 메세지 : 란뽀 : ,이치카와 책")
c.query("새로운 메세지 : 란뽀 : ,다쿠지 책")
c.query("새로운 메세지 : 란뽀 : 필란드 뜻")
c.query("새로운 메세지 : 란뽀 : 더보기 1")
c.query("새로운 메세지 : 란뽀 : 더보기2")
c.query("새로운 메세지 : 란뽀 : 더보기3")
