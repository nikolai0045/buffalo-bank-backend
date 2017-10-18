from django.core.management.base import BaseCommand, CommandError
from bank.models import *
import datetime
import csv

class Command(BaseCommand):

    def handle(self,*args,**kwargs):

        with open('/opt/bank/buffalo-bank-api/second_nine_weeks.csv','rb') as csvfile:
            reader = csv.reader(csvfile)
            for c in Course.objects.all():
                c.active = False
                c.students.clear()
            schedules = Schedule.objects.all()
            for row in reader:
                s_last_name = row[0].strip()
                s_first_name = row[1].strip()
                s_grade = row[2].strip()
                c_number = row[3].strip()
                course_name = row[4].strip()
                t_split = row[5].strip().split(",")
                c_section_number = row[6].strip()
                c_hour = row[7].strip()
                t_first_name = False
                t_last_name = False

            teacher = False
            if len(t_split)>1:
                t_first_name = t_split[1].strip()
                t_last_name = t_split[0].strip()
            if UserProfile.objects.filter(first_name=t_first_name,last_name=t_last_name,user__isnull=False).exists():
                teacher = UserProfile.objects.filter(first_name=t_first_name,last_name=t_last_name,user__isnull=False).first()

            course, created = Course.objects.get_or_create(course_number=c_number,section_number=c_section_number,hour=c_hour)
            if created:
                course.save()
                course.active = True
                course.grade = s_grade
                course.save()
            if teacher and teacher not in course.teachers.all():
                course.teachers.add(teacher)

            student, created = Student.objects.get_or_create(first_name=s_first_name,last_name=s_last_name,grade=s_grade)
            if created:
                student.save()

            print student, course

            course.students.add(student)

            for schedule in schedules:
                if course not in schedule.courses.all():
                    schedule.courses.add(course)
                schedule.save() 
