from CasLogin import CasLogin, test_status

uems_url = 'https://uems.sysu.edu.cn/jwxt/api/sso/cas/login?pattern=student-login'
stu_info_url = 'https://uems.sysu.edu.cn/jwxt/student-status/student-info/detail'
login_status = False # Initialize


if __name__ == '__main__':
    login_cas = CasLogin()
    login_status = test_status(login_cas.main())
    while not login_status:
        login_status = test_status(login_cas.main())  # Retry until Success
    login_to_uems = login_cas.session.get(uems_url, headers=login_cas.headers)
    get_stu_info = login_cas.session.get(stu_info_url, headers=login_cas.headers)
    print(get_stu_info.text)
    login_cas.terminate()  # Stop session, optional.
