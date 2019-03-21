import band_chatbots
import pathlib
from os import rename

# try:
#     if pathlib.Path("update.now").is_file():
#         rename("update.now", "update.complete(change .now for reload)")
#         print("module chatbot reload completed.")
#
# except Exception:
#     pass


c = band_chatbots.ChatBot()
c.get_book("란뽀", "열세 번째 배심원, 스티브 캐버나")
print(c.query("새로운 메세지 : 란뽀 : 얀 제거스 책들"))
print(c.query("새로운 메세지 : 란뽀 : 기울기"))

