# SYSU-CAS
Login to CAS system of SYSU via Python

## Example
(See [example.py](./example.py))
```python
from CasLogin import CasLogin, test_status

target_login_url = 'Your login web page redirecting CAS'
target_url = 'Your target page'
login_status = False  # Initialize


if __name__ == '__main__':
    login_cas = CasLogin()
    login_status = test_status(login_cas.main())
    while not login_status:
        login_status = test_status(login_cas.main())
    # Retry until Success
    
    login_to_target = login_cas.session.get(target_login_url, headers=login_cas.headers)
    get_target = login_cas.session.get(target_url, headers=login_cas.headers)
    print(get_target.text)
    
    login_cas.terminate()
    # Stop session, optional.
```