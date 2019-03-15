import band_chatbots
from selenium import webdriver
import time
import pathlib
import traceback
import importlib
from os import rename
# from selenium.webdriver.common.keys import Keys


if __name__ == '__main__':

    driver = webdriver.Chrome('C:\\zextor\\chromedriver.exe')
    print("CHROMEW DRIVER : ", driver)

    if pathlib.Path("update.now").is_file():
        rename("update.now", "update.complete(change .now for reload)")

    driver.get('https://band.us')
    input("ENTER WHEN READY CHAT ROOM")
    driver.get('https://band.us/band/70571287/chat/CIExV-')
    time.sleep(5)

    c = band_chatbots.ChatBot()
    c.set_driver(driver)

    while True:

        try:

            if pathlib.Path("update.now").is_file():
                # 인스턴스 제거
                band_chatbots.ChatBot.clear_instance()
                # 모듈 교체
                importlib.reload(band_chatbots)
                # 인스턴스 새로 생성
                c = band_chatbots.ChatBot()
                c.set_driver(driver)
                # 파일이름 재설정
                rename("update.now", "update.complete(change .now for reload)")
                print("MODULE RELOADED")

            c.work()

            # sleep interval 1 sec
            time.sleep(1)

        except KeyboardInterrupt:
            print("TERMINATE BY USER REQUESTS")
            exit(1)
        except Exception:
            print("------------{}-----------------".format(time.strftime("%Y-%m-%d %H:%M")))
            traceback.print_exc()
            print("---------------------------------------------")
