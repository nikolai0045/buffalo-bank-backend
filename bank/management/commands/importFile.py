from django.core.management.base import BaseCommand, CommandError
from bank.models import *
import datetime
import csv

class Command(BaseCommand):

    def handle(self,*args,**kwargs):

        with open('/opt/bank/buffalo-bank-api/bank/2018 schedules.csv','rb') as csvfile:
            reader = csv.reader(csvfile)
            monday_schedule = Schedule.objects.get(name__icontains="Monday")
            tuesday_schedule = Schedule.objects.get(name__icontains="Tuesday")
            wednesday_schedule = Schedule.objects.get(name__icontains="Wednesday")
            thursday_schedule = Schedule.objects.get(name__icontains="Thursday")
            friday_schedule = Schedule.objects.get(name__icontains="Friday")

            for c in Course.objects.all():
                c.active = False
                c.students.clear()
            schedules = Schedule.objects.all()
            for s in schedules:
                s.courses.clear()
            for row in reader:
                s_last_name = row[0].strip()
                s_first_name = row[1].strip()
                s_grade = row[2].strip()
                c_number = row[3].strip()
                course_name = row[4].strip()
                t_split = row[5].strip().split(",")
                c_section_number = row[6].strip()
                c_hour = row[9].strip()
                t_first_name = False
                t_last_name = False

                teacher = False
                if len(t_split)>1:
                    t_first_name = t_split[1].strip()
                    t_last_name = t_split[0].strip()
                if UserProfile.objects.filter(first_name=t_first_name,last_name=t_last_name,user__isnull=False).exists():
                    teacher = UserProfile.objects.filter(first_name=t_first_name,last_name=t_last_name,user__isnull=False).first()
                else:
                    teacher = UserProfile(first_name=t_first_name,last_name=t_last_name)
                    teacher.save()

                if len(Course.objects.filter(course_number=c_number,section_number=c_section_number,hour=c_hour)) > 0:
                    courses = Course.objects.filter(course_number=c_number,section_number=c_section_number,hour=c_hour)
                else:
                    for dow in ['Monday','Tuesday','Wednesday','Thursday','Friday']:
                        course, created = Course.objects.get_or_create(name=course_name,course_number=c_number,section_number=c_section_number,hour=c_hour,day_of_week=dow)
                        if created:
                         course.save()
                         course.active = True
                         course.grade = s_grade
                         course.save()
                    if teacher and teacher not in course.teachers.all():
                        course.teachers.add(teacher)
                        course.save()
                    courses = Course.objects.filter(course_number=c_number,section_number=c_section_number,hour=c_hour)

                if len(Student.objects.filter(first_name=s_first_name,last_name=s_last_name,grade=s_grade)) > 1:
                    student = Student.objects.filter(first_name=s_first_name,last_name=s_last_name,grade=s_grade).first()
                else:
                    student, created = Student.objects.get_or_create(first_name=s_first_name,last_name=s_last_name,grade=s_grade)
                    if created:
                        student.save()

                print s_first_name, s_last_name

                for c in courses:
                    c.active = True
                    c.save()
                    c.students.add(student)
                    if c.day_of_week == 'Monday' and c not in monday_schedule.courses.all():
                        monday_schedule.courses.add(c)
                    elif c.day_of_week == 'Tuesday' and c not in tuesday_schedule.courses.all():
                        tuesday_schedule.courses.add(c)
                    elif c.day_of_week == 'Wednesday' and c not in wednesday_schedule.courses.all():
                        wednesday_schedule.courses.add(c)
                    elif c.day_of_week == 'Thursday' and c not in thursday_schedule.courses.all():
                        thursday_schedule.courses.add(c)
                    elif c.day_of_week == 'Friday' and c not in friday_schedule.courses.all():
                        friday_schedule.courses.add(c)