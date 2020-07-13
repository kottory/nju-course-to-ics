from src.courses import CourseSearcher

cs = CourseSearcher('**************', '************')
with open('example.ics', 'wb') as f:
    f.write(cs.createIcs())