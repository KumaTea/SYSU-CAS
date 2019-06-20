# This file will login and get cookie

import requests
import os
from PIL import Image
from bs4 import BeautifulSoup

cas_url = 'https://cas.sysu.edu.cn/cas/login'
captcha_url = 'https://cas.sysu.edu.cn/cas/captcha.jsp'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'Host': 'cas.sysu.edu.cn',
    'Referer': 'https://cas.sysu.edu.cn/',
}


def get_xsrf():
    resp = sysu_cas.get(cas_url, headers=headers, cookies=sysu_cas.cookies.get_dict(), verify=False)
    soup = BeautifulSoup(resp.content, "html.parser")
    xsrf = soup.find('input', attrs={'name': 'execution'}).get("value")
    return xsrf


def get_captcha():
    get_capt = sysu_cas.get(captcha_url, headers=headers, cookies=sysu_cas.cookies.get_dict())
    if not os.path.exists('temp'):
        os.mkdir('temp')
    with open('temp/captcha.jpg', 'wb') as ca:
        ca.write(get_capt.content)
    with Image.open('temp/captcha.jpg') as captcha_image:
        captcha_image.show()
    captcha_code = input('Please input the code in this image:\n')
    os.remove('temp/captcha.jpg')
    return captcha_code


def login(username, password):
    login_data = {
        'username': username,
        'password': password,
        'captcha': get_captcha(),
        'execution': get_xsrf(),
        '_eventId': 'submit',
        'geolocation': '',
    }
    sysu_cas.post(cas_url, headers=headers, cookies=sysu_cas.cookies.get_dict(), data=login_data)
    # print(sysu_cas.cookies.get_dict())
    return sysu_cas.cookies.get_dict()


def test_status(cookies):
    test_web = sysu_cas.get(cas_url, headers=headers, cookies=cookies, verify=False)
    if user_name in test_web.text:
        return True
    else:
        return False


if __name__ == '__main__':
    sysu_cas = requests.Session()
    user_name = input('Please input your NetID:\n')
    user_pass = input('Please input your password:\n')
    login_cookies = login(user_name, user_pass)
    if test_status(login_cookies):
        print('Success!')
    else:
        print('Login Failed.')
    sysu_cas.close()
