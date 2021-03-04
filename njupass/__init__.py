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
        """
        DESCRIPTION:
            Parsing password to encrypted form which can be identified by the backend sersver of UIA.
        ATTRIBUTES:
            password(str): Origin password
        """
        with open(os.path.join(os.path.dirname(__file__), 'resources/encrypt.js')) as f:
            ctx = execjs.compile(f.read())
        return ctx.call('encryptAES', password, self.pwdDefaultEncryptSalt)

    def login(self, username, password):
        """
        DESCRIPTION:
            Post a request for logging in.
        ATTRIBUTES:
            username(str)
            password(str)
        """
        data = {
            'username': username,
            'password': self.parsePassword(password),
            'lt': self.lt,
            'dllt': self.dllt,
            'execution': self.execution,
            '_eventId': self._eventId,
            'rmShown': self.rmShown
        }
        self.session.post(URL_NJU_UIA_AUTH, data=data, allow_redirects=False)


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
