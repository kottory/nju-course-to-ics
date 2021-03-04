from courses import CourseSearcher
from njupass import NjuUiaAuth

auth = NjuUiaAuth('stuid', 'passwd')
cs = CourseSearcher(auth)
with open('example.ics', 'wb') as f:
    f.write(cs.createIcs())