import datetime
from bank.models import *
from tier_two.models import *
from tier_three.models import *

def add_student_to_report(student,report):
    daily_schedule = DailySchedule.objects.filter(date=report.date).first()
    time_slot = daily_schedule.schedule.time_slots.filter(grade=report.course.grade,hour=report.course.hour,start_time=report.start_time).first()
    num_bucks = time_slot.num_bucks
    goals = BehaviorGoal.objects.filter(active=True)

    for i in range(num_bucks):
        deposit = Deposit(
            course_report=report,
            student = student,
            )
        deposit.save()
        for g in goals:
            buck = Buck(
                deposit=deposit,
                goal = g,
                )
            buck.save()
        if student.is_tthree():
            p = student.tthreeprofile_set.first()
            tthree_report, created = TThreeReport.objects.get_or_create(
                report = report,
                profile = p,
                )
            if created:
                tthree_report.save()
        if student.is_ttwo():
            p = s.ttwoprofile_set.first()
            ttwo_goals = p.ttwogoal_set.filter(active=True)
            for g in ttwo_goals:
                ttwo_report, created = TTwoReport.objects.get_or_create(
                    report=report,
                    goal=g,
                    )
                if created:
                    ttwo_report.save()

def add_report_for_today(course):
    today = datetime.date.today()
    daily_schedule = DailySchedule.objects.filter(date=today).first()
    time_slots = daily_schedule.schedule.time_slots.filter(grade=course.grade,hour=course.hour)
    goals = BehaviorGoal.objects.filter(active=True)
    if course not in daily_schedule.schedule.courses.all():
        daily_schedule.schedule.courses.add(course)
        daily_schedule.schedule.save()
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
                print s
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
                    ttwo_goals = p.ttwogoal_set.filter(active=True)
                    for g in ttwo_goals:
                        ttwo_report, created = TTwoReport.objects.get_or_create(
                            report = report,
                            goal = g
                        )
                        if created:
                            ttwo_report.save()

def add_report_for_date(course,date,add_to_schedule):
    daily_schedule = DailySchedule.objects.filter(date=date).first()
    time_slots = daily_schedule.schedule.time_slots.filter(grade=course.grade,hour=course.hour)
    goals = BehaviorGoal.objects.filter(active=True)
    if course not in daily_schedule.schedule.courses.all() and add_to_schedule:
        daily_schedule.schedule.courses.add(course)
        daily_schedule.schedule.save()
    for ts in time_slots:
        hour = ts.hour
        grade = ts.grade
        num_bucks = ts.num_bucks
        start_time = ts.start_time
        end_time = ts.end_time
        report, created = CourseReport.objects.get_or_create(
            date = date,
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
                    ttwo_goals = p.ttwogoal_set.filter(active=True)
                    for g in ttwo_goals:
                        ttwo_report, created = TTwoReport.objects.get_or_create(
                            report = report,
                            goal = g
                        )
                        if created:
                            ttwo_report.save()
