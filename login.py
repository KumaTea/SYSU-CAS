# This file will login and get cookie

import requests
import os
from PIL import Image
from bs4 import BeautifulSoup
from getpass import getpass


class CasLogin:
    cas_url = 'https://cas.sysu.edu.cn/cas/login'
    captcha_url = 'https://cas.sysu.edu.cn/cas/captcha.jsp'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Host': 'cas.sysu.edu.cn',
        'Referer': 'https://cas.sysu.edu.cn/',
    }

    def __init__(self):
        self.session = requests.Session()

    def get_xsrf(self):
        resp = self.session.get(self.cas_url, headers=self.headers, cookies=self.session.cookies.get_dict(), verify=False)
        soup = BeautifulSoup(resp.content, "html.parser")
        xsrf = soup.find('input', attrs={'name': 'execution'}).get("value")
        return xsrf

    def get_captcha(self):
        get_capt = self.session.get(self.captcha_url, headers=self.headers, cookies=self.session.cookies.get_dict())
        if not os.path.exists('temp'):
            os.mkdir('temp')
        with open('temp/captcha.jpg', 'wb') as ca:
            ca.write(get_capt.content)
        with Image.open('temp/captcha.jpg') as captcha_image:
            captcha_image.show()
        captcha_code = input('Please input the code in this image:\n')
        os.remove('temp/captcha.jpg')
        return captcha_code

    def login_cas(self, username, password):
        login_data = {
            'username': username,
            'password': password,
            'captcha': self.get_captcha(),
            'execution': self.get_xsrf(),
            '_eventId': 'submit',
            'geolocation': '',
        }
        result = self.session.post(self.cas_url, headers=self.headers, cookies=self.session.cookies.get_dict(), data=login_data)
        # print(self.session.cookies.get_dict())
        if 'success' in result.text:
            return self.session.cookies.get_dict()
        elif 'credential' in result.text:
            return 'password'
        else:
            return 'captcha'

    def login(self):
        user_name = input('Please input your NetID:\n')
        user_pass = getpass('Please input your password:\n')
        login_result = self.login_cas(user_name, user_pass)
        return login_result


def test_status(result):
    if type(result) == dict:
        print('Success!')
    else:
        if 'captcha' in result:
            print('Maybe captcha is wrong.')
        else:
            print('Maybe password does not match.')
