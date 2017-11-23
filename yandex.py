from selenium import webdriver
import names
import random
import time
import os
import string
import base64
import requests
import json

class  YandexMail:

    apikey = "none"
    mail = ""
    password = ""

    def __init__(self, apikey, mail = None, password = None):
        self.apikey = apikey
        if (mail and password):
            self.mail = mail
            self.password = password


    def gen_pwd(self, length):
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'
        random.seed = (os.urandom(1024))

        return ''.join(random.choice(chars) for i in range(length))

    def create_account(self, save_file = "account.csv"):
        passport_version = False

        driver = webdriver.Firefox()
        driver.get("https://mail.yandex.com/")

        driver.find_element_by_class_name("new-auth-form-button").click()

        first_name = names.get_first_name()
        last_name = names.get_last_name()
        driver.find_element_by_id("firstname").send_keys(first_name)

        driver.find_element_by_id("lastname").send_keys(last_name)
        username = first_name + ''.join(random.choice(string.ascii_lowercase+string.digits) for i in range(10))
        driver.find_element_by_id("login").send_keys(username)
        self.mail = username+"@yandex.com"
        self.password = self.gen_pwd(10)
        driver.find_element_by_id("password").send_keys(self.password)
        driver.find_element_by_id("password_confirm").send_keys(self.password)
        try :
            driver.find_element_by_class_name("human-confirmation-switch-wrap").click()
        except :
            passport_version = True

        if passport_version :
            driver.find_element_by_class_name("link_has-no-phone").click()
            time.sleep(1)
            driver.find_element_by_class_name("registration__label").send_keys("Dark Vador")
            capcha_url = driver.find_element_by_class_name("captcha__image").get_attribute("src")
        else :
            driver.execute_script("document.getElementsByName('hint_question_id')[1].selectedIndex=1")

            driver.find_element_by_id("hint_answer").send_keys("Dark Vador")
            capcha_url = driver.find_element_by_class_name("captcha__captcha__text").get_attribute("src")

        b64_capcha = base64.b64encode(requests.get(capcha_url).content)

        result = requests.post("http://2captcha.com/in.php",
                           data={'method': "base64", 'key': self.apikey, 'body': b64_capcha, 'json' : 1}).text

        id = json.loads(result)['request']

        capcha_text = requests.get("http://2captcha.com/res.php?key=" + self.apikey + "&action=get&id=" + id).text
        while (capcha_text == 'CAPCHA_NOT_READY'):
            time.sleep(5)
            print("2capchat not ready, waiting")
            capcha_text = requests.get("http://2captcha.com/res.php?key=" + self.apikey + "&action=get&id=" + id).text

        if passport_version :
            driver.find_element_by_id("captcha").send_keys(capcha_text)
            driver.find_element_by_class_name("button2_type_submit").click()
        else :
            driver.find_element_by_id("answer").send_keys(capcha_text)
            driver.find_element_by_id("nb-5").click()


        with open(save_file, 'a') as file:
            file.write(self.mail+";"+self.password+"\n")

        driver.close()





