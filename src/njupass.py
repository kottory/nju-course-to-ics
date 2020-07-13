import execjs
import requests
import re
import os

URL_NJU_AUTH = 'https://authserver.nju.edu.cn/authserver/login'


class NjuAuth:
    def __init__(self):
        self.session = requests.Session()
        r = self.session.get(URL_NJU_AUTH)
        self.lt = re.search(
            r'<input type="hidden" name="lt" value="(.*)"/>', r.text).group(1)
        self.dllt = re.search(
            r'<input type="hidden" name="dllt" value="(.*)"/>', r.text).group(1)
        self.execution = re.search(
            r'<input type="hidden" name="execution" value="(.*)"/>', r.text).group(1)
        self._eventId = re.search(
            r'<input type="hidden" name="_eventId" value="(.*)"/>', r.text).group(1)
        self.rmShown = re.search(
            r'<input type="hidden" name="rmShown" value="(.*)"', r.text).group(1)
        self.pwdDefaultEncryptSalt = re.search(
            r'<input type="hidden" id="pwdDefaultEncryptSalt" value="(.*)"', r.text).group(1)

    def parsePassword(self, password):
        with open(os.path.join(os.path.dirname(__file__), 'resources/encrypt.js')) as f:
            ctx = execjs.compile(f.read())
        return ctx.call('encryptAES', password, self.pwdDefaultEncryptSalt)

    def login(self, username, password):
        data = {
            'username': username,
            'password': self.parsePassword(password),
            'lt': self.lt,
            'dllt': self.dllt,
            'execution': self.execution,
            '_eventId': self._eventId,
            'rmShown': self.rmShown
        }
        self.session.post(URL_NJU_AUTH, data=data, allow_redirects=False)