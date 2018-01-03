from django.core.management.base import BaseCommand, CommandError
from bank.models import *
from tier_three.models import *
import datetime

class Command(BaseCommand):

    def handle(self,*args,**kwargs):
        profiles = TThreeProfile.objects.filter(active=True)
        today = datetime.date.today()
        for p in profiles:
            student = p.student
            transactions = student.transaction_set.filter(date__lte=today,date__gte=today-datetime.timedelta(days=5),deposit__isnull=False)
            for t in transactions:
                report = TThreeReport(
                    report = t.deposit.course_report,
                    profile = p
                )
                report.save()