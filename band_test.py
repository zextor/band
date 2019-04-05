import band_chatbots
import pathlib
from os import rename
from selenium import webdriver
# try:
#     if pathlib.Path("update.now").is_file():
#         rename("update.now", "update.complete(change .now for reload)")
#         print("module chatbot reload completed.")
#
# except Exception:
#     pass

driver = webdriver.Chrome('C:\\zextor\\chromedriver.exe')
c = band_chatbots.ChatBot()
c.print_time()
#c.set_driver(driver)
c.query_weather()
c.get_book("r", "메이드인강남")
c.get_translate_to_english("신기신기")
c.send_message("test\n1234\nabcd\n")
c.get_book("란뽀", "도플갱어의 섬, 에도가와 란포")
print(c.query("새로운 메세지 : 란뽀 : 얀 제거스 책들"))
print(c.query("새로운 메세지 : 란뽀 : 기울기"))

