from django.core.management.base import BaseCommand, CommandError
from bank.models import *
import datetime
import csv

class Command(BaseCommand):

    def handle(self,*args,**kwargs):
        today = datetime.date.today()
        daily_schedule = DailySchedule.objects.filter(date = today).first()
        schedule = daily_schedule.schedule
        goals = BehaviorGoal.objects.all()
        for ts in schedule.time_slots.all():
            hour = ts.hour
            grade = ts.grade
            num_bucks = ts.num_bucks
            start_time = ts.start_time
            end_time = ts.end_time
            courses = schedule.courses.filter(grade=grade,hour=hour)
            for c in courses:
                report, created = CourseReport.objects.get_or_create(
                    date = today,
                    course = c,
                    start_time = start_time,
                    end_time = end_time,
                    completed = False
                )
                if created:
                    report.save()

                    for s in c.students.all():
                        for i in range(num_bucks):
                            deposit = Deposit(
                                course_report = report,
                                student = s
                            )
                            deposit.save()
                            for g in goals:
                                buck = Buck(
                                    deposit = deposit,
                                    goal = g
                                )
                                buck.save()
