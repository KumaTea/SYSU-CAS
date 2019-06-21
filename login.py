import requests
import os
import base64
import json
from PIL import Image
from bs4 import BeautifulSoup
from getpass import getpass
import locale


lang_code = locale.getdefaultlocale()[0]

if 'en' in lang_code:
    captcha_alert = 'Please input the code in this image:\n'
    password_alert = 'Please input your password:\n'
    username_alert = 'Please input your NetID:\n'
    item_alert = 'Please input your '
    login_ok = 'Login success!'
    captcha_error = 'Maybe captcha is wrong.'
    password_error = 'Maybe password does not match.'
    success_word = 'success'
else:
    captcha_alert = '请输入验证码（不区分大小写）：\n'
    password_alert = '请输入密码（不显示明文）：\n'
    username_alert = '请输入NetID：\n'
    item_alert = '请输入'
    login_ok = '登录成功！'
    captcha_error = '验证码可能出错，请重试。'
    password_error = '密码可能出错，请重试。'
    success_word = '成功'


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
        captcha_code = input(captcha_alert)
        os.remove('temp/captcha.jpg')
        return captcha_code

    def login(self):
        login_data = {
            'username': get_item('username'),
            'password': get_item('password'),
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
        if success_word in result.text:
            save_item('cookies', json.dumps(self.session.cookies.get_dict()))
            return self.session.cookies.get_dict()
        elif 'credential' in result.text:
            login_fail(True)
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
            return 'success'
        else:
            login_result = self.login()
            return login_result


def test_status(result):
    if type(result) == dict or 'success' in result:
        print(login_ok)
        return True
    else:
        if 'captcha' in result:
            print(captcha_error)
        else:
            print(password_error)
        return False


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
        get_input = getpass(password_alert)
    elif item == 'username':
        get_input = input(username_alert)
    elif item == 'cookies':
        return None
    else:
        get_input = input(item_alert + item + ':\n')
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


def login_fail(critical=False):
    if critical:
        remove_item('username')
        remove_item('password')
    remove_item('cookies')
    return True


if __name__ == '__main__':
    login_cas = CasLogin()
    login_check = login_cas.main()
    test_status(login_check)
    login_cas.terminate()
