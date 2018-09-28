from django.core.management.base import BaseCommand, CommandError
from bank.models import *
from tier_two.models import *
import datetime

class Command(BaseCommand):

    def handle(self,*args,**kwargs):
        profiles = TTwoProfile.objects.filter(active=True)
        today = datetime.date.today()
        for p in profiles:
            goals = p.ttwogoal_set.filter(active=True)
            student = p.student
            transactions = student.transaction_set.filter(date=today,deposit__isnull=False)
            for g in goals:
                for t in transactions:
                    report, created = TTwoReport.objects.get_or_create(
                        report = t.deposit.course_report,
                        goal = g,
                    )
                    if created:
                        report.save()