from django.core.management.base import BaseCommand, CommandError
from bank.models import *
import datetime
import csv

class Command(BaseCommand):

    def handle(self,*args,**kwargs):

        with open('/opt/bank/buffalo-bank-api/bank/3rd nine weeks 2020.csv','rb') as csvfile:
            reader = csv.reader(csvfile)
            mon_schedule = Schedule.objects.get(name__icontains="Monday")
            tues_schedule = Schedule.objects.get(name__icontains="Tuesday")
            weds_schedule = Schedule.objects.get(name__icontains="Wednesday")
            thurs_schedule = Schedule.objects.get(name__icontains="Thursday")
            fri_schedule = Schedule.objects.get(name__icontains="Friday")

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
                c_hour = row[7].strip()
                dow = row[8].strip()
                t_first_name = False
                t_last_name = False

                teacher = False
                if len(t_split)>1:
                    t_first_name = t_split[1].strip()
                    t_last_name = t_split[0].strip()
                if UserProfile.objects.filter(first_name=t_first_name,last_name=t_last_name).exists():
                    teacher = UserProfile.objects.filter(first_name=t_first_name,last_name=t_last_name).first()
                else:
                    teacher = UserProfile(first_name=t_first_name,last_name=t_last_name)
                    teacher.save()


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


                for c in courses:
                    c.active = True
                    c.save()
                    c.students.add(student)
                    if c.day_of_week == 'Monday' and c not in mon_schedule.courses.all():
                        mon_schedule.courses.add(c)
                    elif c.day_of_week == 'Tuesday' and c not in tues_schedule.courses.all():
                        tues_schedule.courses.add(c)
                    elif c.day_of_week == 'Wednesday' and c not in weds_schedule.courses.all():
                        weds_schedule.courses.add(c)
                    elif c.day_of_week == 'Thursday' and c not in thurs_schedule.courses.all():
                        thurs_schedule.courses.add(c)
                    elif c.day_of_week == 'Friday' and c not in fri_schedule.courses.all():
                        fri_schedule.courses.add(c)