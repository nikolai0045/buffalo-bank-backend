from django.core.management.base import BaseCommand, CommandError
from bank.models import *
import datetime
import csv

class Command(BaseCommand):

    def handle(self,*args,**kwargs):
        prepared, created = BehaviorGoal.objects.get_or_create(goal="Be Prepared")
        if created:
            prepared.save()
        on_task, created = BehaviorGoal.objects.get_or_create(goal="Be On Task")
        if created:
            on_task.save()
        respectful, created = BehaviorGoal.objects.get_or_create(goal="Be Respectful")
        if created:
            respectful.save()

        with open('/opt/bank/buffalo-bank-api/bank/schedules.csv','rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                s_last_name = row[0]
                s_first_name = row[1]
                s_grade = row[2]
                c_number = row[3]
                c_name = row[4]
                try:
                    t_split = row[5].split(",")
                except:
                    pass
                teacher = False
                print t_split
                if len(t_split)>1:
                    t_first_name = t_split[1]
                    t_last_name = t_split[0]
                    teacher, created = UserProfile.objects.get_or_create(first_name=t_first_name,last_name=t_last_name)
                    if created:
                        teacher.save()
                c_section_number = row[6]
                c_hour = row[7]
                course, created = Course.objects.get_or_create(name=c_name,course_number=c_number,section_number=c_section_number,hour=c_hour)
                if created:
                    course.save()
                if teacher and teacher not in course.teachers.all():
                    course.teachers.add(teacher)
                c_raw_start_time = row[12]
                c_raw_end_time = row[13]
                weekdays = [x for x in row[14].split(',')]

                student, created = Student.objects.get_or_create(first_name=s_first_name,last_name=s_last_name,grade=s_grade)
                if created:
                    student.save()

                goals = BehaviorGoal.objects.all()
		today = datetime.date.today()
		if course.name != "PLT":
			course_report, create = CourseReport.objects.get_or_create(course=course,date=today,start_time=datetime.datetime.strptime(c_raw_start_time,'%H:%M'),end_time=datetime.datetime.strptime(c_raw_end_time,'%H:%M'))
			if create:
				course_report.save()
			deposit, created = Deposit.objects.get_or_create(student=student,date=today,course_report=course_report)
			if created:
				deposit.save()
			for g in goals:
				buck, created = Buck.objects.get_or_create(deposit=deposit,goal=g)
				if created:
					buck.save()
                if len(weekdays) == 0:
                    for date in [datetime.date(2017,8,14),datetime.date(2017,8,15),datetime.date(2017,8,16),datetime.date(2017,8,17),datetime.date(2017,8,18)]:
                        course_report, created = CourseReport.objects.get_or_create(course=course,date=date,start_time=datetime.datetime.strptime(c_raw_start_time,'%H:%M'),end_time=datetime.datetime.strptime(c_raw_end_time,'%H:%M'))
                        if created:
                            course_report.save()
                        deposit, created = Deposit.objects.get_or_create(student=student,date=date,course_report=course_report)
                        if created:
                            deposit.save()
                        for g in goals:
                            buck, created = Buck.objects.get_or_create(deposit=deposit,goal=g)
                            if created:
                                buck.save()
                elif len(weekdays) == 4:
                    for date in [datetime.date(2017,8,14),datetime.date(2017,8,15),datetime.date(2017,8,17),datetime.date(2017,8,18)]:
                        course_report, created = CourseReport.objects.get_or_create(course=course,date=date,start_time=datetime.datetime.strptime(c_raw_start_time,'%H:%M'),end_time=datetime.datetime.strptime(c_raw_end_time,'%H:%M'))
                        if created:
                            course_report.save()
                        deposit, created = Deposit.objects.get_or_create(student=student,date=date,course_report=course_report)
                        if created:
                            deposit.save()
                        for g in goals:
                            buck, created = Buck.objects.get_or_create(deposit=deposit,goal=g)
                            if created:
                                buck.save()
                elif len(weekdays) == 1:
                    for date in [datetime.date(2017,8,16)]:
                        course_report, created = CourseReport.objects.get_or_create(course=course,date=date,start_time=datetime.datetime.strptime(c_raw_start_time,'%H:%M'),end_time=datetime.datetime.strptime(c_raw_end_time,'%H:%M'))
                        if created:
                            course_report.save()
                        deposit, created = Deposit.objects.get_or_create(student=student,date=date,course_report=course_report)
                        if created:
                            deposit.save()
                        for g in goals:
                            buck, created = Buck.objects.get_or_create(deposit=deposit,goal=g)
                            if created:
                                buck.save()
