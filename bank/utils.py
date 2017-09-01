import datetime
from bank.models import *
from tier_two.models import *
from tier_three.models import *

def add_report_for_today(course):
	today = datetime.date.today()
	daily_schedule = DailySchedule.objects.filter(date=today).first()
	time_slots = daily_schedule.time_slots.filter(grade=course.grade,hour=course.hour)
    if course not in daily_schedule.courses.all():
        daily_schedule.courses.add(course)
        daily_schedule.save()
	for ts in time_slots:
		hour = ts.hour
		grade = ts.grade
		num_bucks = ts.num_bucks
		start_time = ts.start_time
		end_time = ts.end_time
		report, created = CourseReport.objects.get_or_create(
			date = today,
			course = course,
			start_time = start_time,
			end_time = end_time,
			completed = False
		)
		if created:
			report.save()

			for s in course.students.all():
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
				if s.is_tthree():
					p = s.tthreeprofile_set.first()
					tthree_report, created = TThreeReport.objects.get_or_create(
						report = report,
						profile = p
					)
					if created:
						tthree_report.save()
				if s.is_ttwo():
					p = s.ttwoprofile_set.first()
					goals = p.ttwogoal_set.filter(active=True)
					for g in goals:
						ttwo_report, created = TTwoProfile.objects.get_or_create(
							report = report,
							goal = g
						)
						if created:
							report.save()
