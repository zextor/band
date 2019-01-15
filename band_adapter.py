from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import band_chatbots
import pprint
import pathlib
import importlib
from os import rename
import schedule

"""
    refresh interval for heavy browser
"""
REFRESH_INTERVAL = 5.0

def refresh():
    """
        refresh chrome browser
    :return:
    """
    driver.refresh()

def get_driver():
    """
        return webdriver instance
    :return: webdriver
    """
    return driver

def send_message(text):
    """
        Send Text to Browser
        :param  text for send
        :returns none
    """
    if len(text) > 0:
        driver.find_element_by_xpath('//*[@id="write_comment_view81"]').send_keys(text)

        if not text.endswith("\n"):
            driver.find_element_by_xpath('//*[@id="write_comment_view81"]').send_keys("\n")
    # no need click send-button
    # text will send, if ends with "\n"
    # driver.find_element_by_xpath('//*[@id="wrap"]/div[3]/div/div/div[2]/div[2]/button').click()


def get_new_message():
    """
        Get New Text from Browser
        :returns New Message
    """
    last_message = None
    try:
        last_message = (BeautifulSoup(driver.page_source, 'html.parser').find('div', {'class': '_recieveMessage'})).text
    except AttributeError:
        last_message = ""
        pass
    return last_message


def alarm_new_book():
    send_message(c.query_new_book(driver))


def alarm_weather():
    send_message(c.query_weather())


def alarm_keywords():
    send_message(c.query_keywords())


if __name__ == '__main__':

    driver = webdriver.Chrome('C:\\zextor\\chromedriver.exe')
    print("Webdriver : ", driver)
    driver.get('https://band.us/band/73188261/chat/CL1Vt8')

    new_message = None
    old_message = None

    c = band_chatbots.ChatBot()
    c.register_callback_sendmessage(send_message)
    c.register_callback_refresh(refresh)
    c.register_callback_getdriver(get_driver)

    print(driver.current_window_handle)

    input("Enter after login process...")

    schedule.every().hour.do(alarm_new_book)
    schedule.every().day.at("05:30").do(refresh)
    schedule.every().day.at("07:30").do(alarm_weather)
    schedule.every().day.at("08:00").do(send_message, "좋은 하루 보내세요~ ❤")
    schedule.every().day.at("12:00").do(send_message, "점심 맛있게 드세요~ ❤")
    schedule.every().day.at("18:00").do(send_message, "여유로운 저녁 보내세요~ ❤")
    schedule.every().day.at("23:00").do(send_message, "고운밤 되세요~ ❤")
    schedule.every().day.at("00:00").do(alarm_keywords)
    schedule.every().day.at("06:00").do(alarm_keywords)
    schedule.every().day.at("09:00").do(alarm_keywords)
    schedule.every().day.at("11:00").do(alarm_keywords)
    schedule.every().day.at("13:00").do(alarm_keywords)
    schedule.every().day.at("15:00").do(alarm_keywords)
    schedule.every().day.at("17:00").do(alarm_keywords)
    schedule.every().day.at("19:00").do(alarm_keywords)
    schedule.every().day.at("21:00").do(alarm_keywords)

    while True:

        try:
            # get new message
            new_message = get_new_message()

            if len(new_message) > 0:
                # if new message
                if new_message != old_message:
                    reply = c.query(new_message)
                    send_message(reply)
                    old_message = new_message

            if pathlib.Path("update.now").is_file():
                importlib.reload(band_chatbots)
                c = band_chatbots.ChatBot()
                c.register_callback_sendmessage(send_message)
                c.register_callback_refresh(refresh)
                c.register_callback_getdriver(get_driver)

                rename("update.now", "update.complete(change .now for reload)")
                print("Module chatbot Reload Completed!")

            # sleep interval 1 sec
            schedule.run_pending()
            time.sleep(1)
        except AttributeError:
            print("AttributeError Error")
            pass
        except KeyboardInterrupt:
            print("Terminate by user requests.")
            exit(1)
        except Exception as e:
            pprint.pprint(e)
            pass
