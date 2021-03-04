import getpass
import njupass
from courses import CourseSearcher
from PIL import Image

auth = njupass.NjuUiaAuth()

while True:
    auth = njupass.NjuUiaAuth()
    username = input("Please Input Your User Name(required): ")
    password = getpass.getpass("Please Input Your Password(required): ")
    captchaResponse = ''

    needCaptcha = auth.needCaptcha(username)

    if needCaptcha:
        img = Image.open(auth.getCaptchaCode())
        img.show()
        captchaResponse = input("Please Input Captcha Code: ")

    if auth.login(username, password, captchaResponse):
        print("Login Success!")
        break
    else:
        print("Please Try Again!")

filename = input("Please Input iCal fle name(default example.ics): ")
if filename == '':
    filename = 'example.ics'

cs = CourseSearcher(auth)

with open(filename, 'wb') as f:
    f.write(cs.createIcs())



