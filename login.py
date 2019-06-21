import requests
import os
import base64
import json
from PIL import Image
from bs4 import BeautifulSoup
from getpass import getpass


class CasLogin:
    cas_url = 'https://cas.sysu.edu.cn/cas/login'
    captcha_url = 'https://cas.sysu.edu.cn/cas/captcha.jsp'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        # 'Host': 'cas.sysu.edu.cn',
        # 'Referer': 'https://cas.sysu.edu.cn/',
    }

    def __init__(self):
        self.session = requests.Session()
        self.username = get_item('username')
        self.password = get_item('password')

    def get_xsrf(self):
        resp = self.session.get(self.cas_url, headers=self.headers, cookies=self.session.cookies.get_dict())
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

    def login(self):
        login_data = {
            'username': self.username,
            'password': self.password,
            'captcha': self.get_captcha(),
            'execution': self.get_xsrf(),
            '_eventId': 'submit',
            'geolocation': '',
        }
        if get_item('cookies'):
            cookies_file = get_item('cookies')
        else:
            cookies_file = self.session.cookies.get_dict()
        result = self.session.post(self.cas_url, headers=self.headers, cookies=cookies_file, data=login_data)
        # print(self.session.cookies.get_dict())
        if 'success' in result.text:
            save_item('cookies', json.dumps(self.session.cookies.get_dict()))
            return self.session.cookies.get_dict()
        elif 'credential' in result.text:
            login_fail()
            return 'password'
        else:
            login_fail()
            return 'captcha'

    def check_status(self):
        resp = self.session.get(self.cas_url, headers=self.headers, cookies=self.session.cookies.get_dict())
        if 'success' in resp.text:
            return True
        else:
            return False

    def terminate(self):
        self.session.close()
        return True

    def main(self):
        if self.check_status():
            return 'Already logged'
        else:
            login_result = self.login()
            return login_result


def test_status(result):
    if type(result) == dict or 'Already' in result:
        print('Success!')
    else:
        if 'captcha' in result:
            print('Maybe captcha is wrong.')
        else:
            print('Maybe password does not match.')


def get_item(item, decode='base64', ext='txt'):
    if ext:
        filename = item + '.' + ext
    else:
        filename = item

    if os.path.isfile(filename):
        if decode:
            with open(filename, 'rb') as file:
                read_file = base64.b64decode(file.read())
        else:
            with open(filename, 'r') as file:
                read_file = file.read()
        if item == 'cookies':
            read_file = json.loads(read_file)
        return read_file

    if item == 'password':
        get_input = getpass('Please input your password:\n')
    elif item == 'username':
        get_input = input('Please input your NetID:\n')
    elif item == 'cookies':
        return None
    else:
        get_input = input('Please input your ' + item + ':\n')
    save_item(item, get_input, 'base64')
    return get_input


def save_item(name, content, encode='base64', ext='txt'):
    if ext:
        filename = name + '.' + ext
    else:
        filename = name
    if encode:
        with open(filename, 'wb') as file:
            save = base64.b64encode(bytes(content, 'utf-8'))
            file.write(save)
    else:
        with open(filename, 'w') as file:
            save = content
            file.write(save)
    return True


def remove_item(name, ext='txt'):
    if ext:
        filename = name + '.' + ext
    else:
        filename = name
    if os.path.isfile(filename):
        os.remove(filename)
    return True


def login_fail():
    remove_item('username')
    remove_item('password')
    remove_item('cookies')
    return True


if __name__ == '__main__':
    login_cas = CasLogin()
    login_check = login_cas.main()
    test_status(login_check)
    login_cas.terminate()
