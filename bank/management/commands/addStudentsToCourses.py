from django.core.management.base import BaseCommand, CommandError
from bank.models import *
import datetime

class Command(BaseCommand):

    def handle(self,*args,**kwargs):
    	reports = CourseReport.objects.filter(date=datetime.date.today())

    	for r in reports:
    		for d in r.deposit_set.all():
    			student = d.student
    			course = r.course
    			if student not in course.students.all():
    				course.students.add(student)
    				course.save()