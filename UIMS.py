from hashlib import md5
import requests
import json


def transfer(username, password):
    j_password = md5(('UIMS' + username + password).encode()).hexdigest()
    pwd_strenth = 0
    if len(password) < 4 or username == password or password == '000000':
        pass
    else:
        if any(map(lambda x:x.isdigit(), password)):
            pwd_strenth += 1
        if any(map(lambda x:x.isalpha(), password)):
            pwd_strenth += 1
        if not password.isalnum():
            pwd_strenth += 1
        if len(password) < 6 and pwd_strenth:
            pwd_strenth -= 1
    return j_password, pwd_strenth


class UIMS(object):
    def __init__(self, user, pwd):
        self.session = requests.session()
        self.login(user, pwd)

    def login(self, username, password):
        s = self.session
        s.get('http://uims.jlu.edu.cn/ntms/')
        j_password, pwd_strength = transfer(username, password)
        cookies = {
            'loginPage': 'userLogin.jsp',
            'alu': username,
            'pwdStrength': '2',
        }
        requests.utils.add_dict_to_cookiejar(s.cookies, cookies)

        post_data = {
            'j_username': username,
            'j_password': j_password,
            'mousePath': pwd_strength
        }
        s.post('http://uims.jlu.edu.cn/ntms/j_spring_security_check', data=post_data)

    def get_course(self):
        s = self.session
        r = s.post('http://uims.jlu.edu.cn/ntms/action/getCurrentUserInfo.do')
        user_info = json.loads(r.text)
        post_data = {
            "tag": "search@teachingTerm",
            "branch": "byId",
            "params": {
                "termId": user_info['defRes']['term_l']
            }
        }
        headers = {'Content-Type': 'application/json'}
        r = s.post('http://uims.jlu.edu.cn/ntms/service/res.do', json.dumps(post_data), headers=headers)
        start_date = json.loads(r.text)['value'][0]['startDate'].split('T')[0]

        post_data["params"]["studId"] = user_info['userId']
        post_data["branch"] = "default"
        post_data["tag"] = "teachClassStud@schedule"
        r = s.post('http://uims.jlu.edu.cn/ntms/service/res.do', json.dumps(post_data), headers=headers)
        return start_date, json.loads(r.text)['value']


if __name__ == '__main__':
    # user, pwd = input().split(',')
    user, pwd = '52151126', '11171x'
    print(UIMS(user, pwd).get_course())

