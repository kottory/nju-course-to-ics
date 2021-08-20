"""
DESCRIPTION:
    Tools for getting Authorization websites of Nanjing University
PACKAGES:
    NjuUiaAuth
    NjuEliteAuth
"""
import execjs
import requests
import re
import os
from io import BytesIO

URL_NJU_UIA_AUTH = 'https://authserver.nju.edu.cn/authserver/login'
URL_NJU_ELITE_LOGIN = 'http://elite.nju.edu.cn/jiaowu/login.do'


class NjuUiaAuth:
    """
    DESCRIPTION:
        Designed for passing Unified Identity Authentication(UIA) of Nanjing University.
    """

    def __init__(self):
        self.session = requests.Session()
        r = self.session.get(URL_NJU_UIA_AUTH)
        self.lt = re.search(
            r'<input type="hidden" name="lt" value="(.*)"/>', r.text).group(1)
        self.execution = re.search(
            r'<input type="hidden" name="execution" value="(.*)"/>', r.text).group(1)
        self._eventId = re.search(
            r'<input type="hidden" name="_eventId" value="(.*)"/>', r.text).group(1)
        self.rmShown = re.search(
            r'<input type="hidden" name="rmShown" value="(.*)"', r.text).group(1)
        self.pwdDefaultEncryptSalt = re.search(
            r'<input type="hidden" id="pwdDefaultEncryptSalt" value="(.*)"', r.text).group(1)

    def getCaptchaCode(self):
        """
        DESCRIPTION:
            Getting captcha code binded with IP
        RETURN_VALUE:
            captcha code image(ByteIO). Recommended using Image.show() in PIL.
        """
        url = 'https://authserver.nju.edu.cn/authserver/captcha.html'
        res = self.session.get(url, stream=True)
        return BytesIO(res.content)


    def parsePassword(self, password):
        """
        DESCRIPTION:
            Parsing password to encrypted form which can be identified by the backend sersver of UIA.
        ATTRIBUTES:
            password(str): Original password
        """
        with open(os.path.join(os.path.dirname(__file__), 'resources/encrypt.js')) as f:
            ctx = execjs.compile(f.read())
        return ctx.call('encryptAES', password, self.pwdDefaultEncryptSalt)

    
    def needCaptcha(self, username):
        url = 'https://authserver.nju.edu.cn/authserver/needCaptcha.html?username={}'.format(username)
        r = self.session.post(url)
        if 'true' in r.text:
            return True
        else:
            return False


    def login(self, username, password, captchaResponse=""):
        """
        DESCRIPTION:
            Post a request for logging in.
            Return true if login success, false otherwise
        ATTRIBUTES:
            username(str)
            password(str)
        """
        data = {
            'username': username,
            'password': self.parsePassword(password),
            'lt': self.lt,
            'dllt': 'userNamePasswordLogin',
            'execution': self.execution,
            '_eventId': self._eventId,
            'rmShown': self.rmShown,
            'captchaResponse': captchaResponse,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome"
        }
        r = self.session.post(URL_NJU_UIA_AUTH, data=data, allow_redirects=False)
        print(data)
        print(r.text)
        return r.status_code == 302


class NjuEliteAuth:
    """
    DESCRIPTION:
        Designed for passing Unified Identity Authentication(UIA) of Nanjing University.
    """

    def __init__(self):
        self.session = requests.session()

    def getValidateCode(self):
        """
        DESCRIPTION:
            Getting validate code binded with IP
        RETURN_VALUE:
            validate code image(ByteIO). Recommended using Image.show() in PIL.
        """
        url = 'http://elite.nju.edu.cn/jiaowu/ValidateCode.jsp'
        res = self.session.get(url, stream=True)
        return BytesIO(res.content)

    def login(self, userName, password, validateCode):
        """
        DESCRIPTION:
            Post a request for logging in.
        ATTRIBUTES:
            username(str)
            password(str)
            validateCode(str)
        """
        self.session.post(URL_NJU_ELITE_LOGIN, data={
            'userName': userName,
            'password': password,
            'ValidateCode': validateCode
        })
