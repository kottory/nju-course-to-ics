import json
import pytz
import re
from datetime import date, datetime, time, timedelta
from njupass import NjuUiaAuth
from icalendar import Calendar, Event, vText

TIME_START_CLASS = {
    1: time(8, 0),
    2: time(9, 0),
    3: time(10, 10),
    4: time(11, 10),
    5: time(14, 0),
    6: time(15, 0),
    7: time(16, 10),
    8: time(17, 10),
    9: time(18, 30),
    10: time(19, 30),
    11: time(20, 30),
    12: time(21, 30)
}

TIME_END_CLASS = {
    1: time(8, 50),
    2: time(9, 50),
    3: time(11, 0),
    4: time(12, 0),
    5: time(14, 50),
    6: time(15, 50),
    7: time(17, 0),
    8: time(18, 0),
    9: time(19, 20),
    10: time(20, 20),
    11: time(21, 20),
    12: time(22, 20)
}


def getNjuClassesUrl(date=date.today()):
    """url of classes information"""
    return 'https://wx.nju.edu.cn/njukb/wap/default/classes?date={}'.format(str(date))


def getFirstDay(curDate, curWeek):
    """get first day of the first week"""
    assert(curWeek >= 1)
    curDate -= timedelta(weeks=curWeek-1)
    curDate -= timedelta(weeks=curDate.weekday())
    return curDate


def combineDateAndTime(d, t):
    """combine date and time to datetime"""
    return datetime(d.year, d.month, d.day, t.hour, t.minute, t.second, tzinfo=pytz.timezone('Asia/Shanghai'))


def parseCourse(course, curDate):
    """parse course information from json to vEVENT of ics"""
    st = int(course['order'])
    ed = st + int(course['totalLength']) - 1
    event = Event()
    event.add('summary', course['course_name'])
    event.add('property', 5)
    event.add('sequence', 0)
    event.add('dtstart', combineDateAndTime(curDate, TIME_START_CLASS[st]))
    event.add('dtend', combineDateAndTime(curDate, TIME_END_CLASS[ed]))
    event.add('dtstamp', datetime.today())
    event['location'] = vText(course['location'])
    event['uid'] = course['course_id']
    event['status'] = vText('CONFIRMED')
    event['description'] = vText('教师: {}'.format(course['teacher']))
    return event


class CourseSearcher:
    def __init__(self, username, password):
        self.auth = NjuUiaAuth()
        self.auth.login(username, password)

    def createIcs(self, maxWeek=20):
        events = []
        data = json.loads(self.auth.session.get(getNjuClassesUrl()).content)

        curWeek = int(re.search(r'第(\d{1,2})周',
                                data['d']['dateInfo']['name']).group(1))
        firstDay = getFirstDay(date.today(), curWeek)
        mondays = [firstDay + timedelta(weeks=x) for x in range(maxWeek)]

        for monday in mondays:
            data = json.loads(self.auth.session.get(
                getNjuClassesUrl(monday)).content)['d']
            if data['noClasses'] == 'true':
                continue
            for x in range(1, 8):
                classDate = monday + timedelta(x - 1)
                for course_list in data['kclist'][str(x)].values():
                    if course_list:
                        events.append(parseCourse(course_list[0], classDate))

        cal = Calendar()
        cal.add('prodid', 'NJU COURSE TO ICS by qqktr')
        cal.add('version', '2.0')
        for event in events:
            cal.add_component(event)

        return cal.to_ical()
