import band_chatbots
import pathlib
from os import rename

def cb(text):
    print(text)

def rf():
    print("refresh")

def gd():
    print("get driver, return null")
    return None


# try:
#     if pathlib.Path("update.now").is_file():
#         rename("update.now", "update.complete(change .now for reload)")
#         print("module chatbot reload completed.")
#
# except Exception:
#     pass


c = band_chatbots.ChatBot()
c.register_callback_sendmessage(cb)
c.register_callback_refresh(rf)
c.register_callback_getdriver(gd)
#c.query_weather()
#c.query_keywords()
#c.query_new_book()
#c.query_tv_rating()
# test

print(c.query("새로운 메세지 : 란뽀 : 뽀봇 느려"))
print(c.query("새로운 메세지 : 란뽀 : 기울기"))
#print(c.query("새로운 메세지 : 란뽀 : 날씨"))
#print(c.query("새로운 메세지 : 란뽀 :  2800*0.6 ="))
#print(c.query("새로운 메세지 : 란뽀 : 기중기"))
#print(c.query("새로운 메세지 : 란뽀 : 기울기"))
#print(c.query("새로운 메세지 : 란뽀 : 기중기"))
#print(c.query("새로운 메세지 : 란뽀 : 체근근"))
#print(c.query("새로운 메세지 : 란네 : 끝말잇기"))

