# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.six import BytesIO

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView, CreateAPIView, DestroyAPIView
from rest_framework import status, authentication, permissions, viewsets
from rest_framework.parsers import JSONParser

from jsonview.decorators import json_view

from .serializers import (
	CourseReportSerializer,
	CourseStudentsSerializer,
	BasicCourseSerializer,
	FullCourseReportSerializer,
	BehaviorGoalSerializer,
	MissingAssignmentSerializer,
	BasicStudentSerializer,
	StudentDepositSerializer,
	StudentPersonalBehaviorGoalSerializer,
	TTwoReportSerializer,
	TThreeReportSerializer,
	CreateStudentPersonalBehaviorGoalSerializer,
	MissingAssignmentSerializer,
	InitPersonalBehaviorGoalSerializer,
	TTwoGoalSerializer,
	TThreeGoalSerializer,
	TTwoReportNoteSerializer,
	TThreeReportNoteSerializer,
	PurchaseItemSerializer,
	CourseMissingAssignmentSerializer,
	TimeSlotSerializer,
	DailyScheduleSerializer,
	ScheduleSerializer,
	DepositNotesSerializer,
	AbsenceSerializer
)
from .models import (
	CourseReport,
	Course,
	BehaviorGoal,
	MissingAssignment,
	Student,
	PersonalBehaviorGoal,
	Deposit,
	Buck,
	UserProfile,
	PurchaseItem,
	Purchase,
	TimeSlot,
	Schedule,
	DailySchedule,
	Absence
)
from tier_two.models import TTwoReport
from tier_three.models import TThreeReport

class RetrievePurchaseItemsView(ListAPIView):
	model = PurchaseItem
	serializer_class = PurchaseItemSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	queryset = PurchaseItem.objects.all()

class RetrievePurchaseItemsByPrice(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def get(self,request,*args,**kwargs):
		response = []
		items = PurchaseItem.objects.filter(quantity_remaining__gte=1).order_by('current_price')
		current_block = {
			'price':items[0].current_price,
			'items':[]
		}
		for item in items:
			if current_block['price'] != item.current_price:
				response.append(current_block)
				current_block = {
					'price':item.current_price,
					'items':[]
				}
			current_block['items'].append(PurchaseItemSerializer(item)).data
		return Response(response)

class CreatePurchaseItemView(CreateAPIView):
	model = PurchaseItem
	serializer_class = PurchaseItemSerializer
	authentication_classes = (authentication.TokenAuthentication,)

class DeletePurchaseItemView(DestroyAPIView):
	model = PurchaseItem
	serializer_class = PurchaseItemSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	queryset = PurchaseItem.objects.all()

class UpdatePurchaseItemView(UpdateAPIView):
	model = PurchaseItem
	serializer_class = PurchaseItemSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	queryset = PurchaseItem.objects.all()

class SubmitTransactionView(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		raw_students = data['selectedStudents']
		raw_items = data['selectedItems']
		students = []
		items = []
		for s in raw_students:
			students.append(Student.objects.get(pk=s['id']))
		for i in raw_items:
			items.append(PurchaseItem.objects.get(pk=i['id']))
		for s in students:
			for i in items:
				new_purchase = Purchase(item=i,student=s,price=i.current_price)
				new_purchase.save()
				s.account_balance = s.account_balance - new_purchase.price
				i.quantity_remaining -= 1
				i.save()
				s.save()
		return Response({'Transaction':'success'})

class RetrieveReportsView(ListAPIView):
    serializer_class = CourseReportSerializer
    authentication_classes = (authentication.TokenAuthentication,)

    def dispatch(self,request,*args,**kwargs):
        self.day = int(kwargs.pop('day',False))
        self.month = int(kwargs.pop('month',False))
        self.year = int(kwargs.pop('year',False))
        return super(RetrieveReportsView,self).dispatch(request,*args,**kwargs)

    def get_queryset(self):
        if not self.day and not self.month and not self.year:
            date = datetime.date.today()
        else:
            date = datetime.date(self.year,self.month,self.day)

        if self.request.user.userprofile.user_type == 'ADMIN':
            return CourseReport.objects.filter(date=date)

        else:
            return CourseReport.objects.filter(date=date,course__teachers=self.request.user.userprofile)

class MarkReportInactiveView(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		report_id = data['id']
		course_id = data['course']['id']
		report = CourseReport.objects.get(pk=report_id)
		if report.completed:
			for deposit in report.deposit_set.all():
				student = deposit.student
				student.account_balance -= deposit.amount_earned
				student.save()
		report.delete()
		course = Course.objects.get(pk=course_id)
		course.active = False
		course.save()
		return BasicCourseSerializer(course).data

class RemoveReportView(DestroyAPIView):
	model = CourseReport
	serializer_class = CourseReportSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	queryset = CourseReport.objects.all()

	def destroy(self,request,*args,**kwargs):
		report = CourseReport.objects.get(pk=kwargs.pop('pk'))
		schedule = Schedule.objects.filter(date = datetime.date.today()).first()
		schedule.courses.remove(report.course)
		report.delete()
		schedule.save()
		response = Response()
		response.status_code = 204
		return response

class GetStudentsByGrade(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		print data
		grade = data['grade']
		students = Student.objects.filter(grade=grade)
		return Response(BasicStudentSerializer(students,many=True).data)

class AddStudentToCourseReport(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		student_id = data['student_id']
		student = Student.objects.get(pk=student_id)
		report_id = data['report_id']
		report = CourseReport.objects.get(pk=report_id)
		date = datetime.date.today()
		goals = BehaviorGoal.objects.all()

		if student not in report.course.students.all():
			old_courses = student.course_set.filter(hour=report.course.hour,active=True)
			for c in old_courses:
				c.students.remove(student)

			deposit = Deposit(
				student = student,
				course_report = report,
			)

			deposit.save()

			for g in goals:
				buck = Buck(
					goal = g,
					deposit = deposit,
				)

				buck.save()

			if student.is_ttwo():
				for g in student.ttwoprofile_set.first().ttwogoal_set.all():
					ttworeport = TTwoReport(
						report = report,
						goal = g,
					)
					ttworeport.save()

			if student.is_tthree():
				tthreereport = TThreeReport(
					report = report,
					profile = student.tthreeprofile_set.first(),
				)
				tthreereport.save()

		return Response({'success':True})

class RemoveStudentFromCourseReport(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		student_id = data['student_id']
		student = Student.objects.get(pk=student_id)
		report_id = data['report_id']
		report = CourseReport.objects.get(pk=report_id)
		date = datetime.date.today()

		deposits = Deposit.objects.filter(course_report=report,student=student)
		for d in deposits:
			d.delete()
		if student.is_ttwo():
			ttworeports = TTwoReport.objects.filter(report=report,goal__profile__student=student)
			for t in ttworeports:
				t.delete()
		if student.is_tthree():
			tthreereports = TThreeReport.objects.filter(report=report,profile__student=student)
			for t in tthreereports:
				t.delete()

		course = report.course
		course.students.remove(student)
		course.save()
		student.save()
		return Response({'removed':True})

class RetrieveActiveCoursesView(ListAPIView):
    serializer_class = BasicCourseSerializer
    authentication_classes = (authentication.TokenAuthentication,)

    def get_queryset(self):
        if self.request.user.userprofile.user_type == 'ADMIN':
            return Course.objects.filter(active=True)
        else:
            two_weeks_ago = datetime.date.today()-datetime.timedelta(days=14)
            courses = self.request.user.userprofile.course_set.filter(active=True)
            return courses

class SearchCoursesView(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		queryset = Course.objects.all()
		if data['active']:
			queryset = queryset.filter(active=data['active'])
		if data['hour']:
			queryset = queryset.filter(hour=data['hour'])
		if data['grade']:
			for c in queryset:
				if c.students.first().grade != data['grade']:
					queryset = queryset.exclude(pk=c.pk)
		return Response(BasicCourseSerializer(queryset,many=True).data)

class RetrieveAllCoursesView(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def get(self,request,*args,**kwargs):
		courses = Course.objects.filter(active=True)
		return Response(BasicCourseSerializer(courses,many=True).data)

class RetrieveStudentsByCourseView(RetrieveAPIView):
    model = Course
    serializer_class = CourseStudentsSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    queryset = Course.objects.all()

class RetrieveCourseReportView(RetrieveAPIView):
    model = CourseReport
    serializer_class = FullCourseReportSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    queryset = CourseReport.objects.all()

class UpdateCourseReportView(UpdateAPIView):
    model = CourseReport
    serializer_class = FullCourseReportSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    queryset = CourseReport.objects.all()

class InitPersonalBehaviorGoalView(CreateAPIView):
	model = PersonalBehaviorGoal
	serializer_class = InitPersonalBehaviorGoalSerializer
	authentication_classes = (authentication.TokenAuthentication,)

class DestroyPersonalBehaviorGoalView(DestroyAPIView):
	model = PersonalBehaviorGoal
	serializer_class = InitPersonalBehaviorGoalSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	queryset = PersonalBehaviorGoal.objects.all()

class UpdatePersonalBehaviorGoalView(UpdateAPIView):
	model = PersonalBehaviorGoal
	serializer_class = StudentPersonalBehaviorGoalSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	queryset = PersonalBehaviorGoal.objects.all()

class CreatePersonalBehaviorGoalView(CreateAPIView):
	model = PersonalBehaviorGoal
	serializer_class = CreateStudentPersonalBehaviorGoalSerializer
	authentication_classes = (authentication.TokenAuthentication,)

class RetrieveBehaviorGoalsView(ListAPIView):
	model = BehaviorGoal
	serializer_class = BehaviorGoalSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	queryset = BehaviorGoal.objects.filter(active=True)

class RetrieveCourseMissingWorkView(ListAPIView):
	model = MissingAssignment
	serializer_class = CourseMissingAssignmentSerializer
	authentication_class = (authentication.TokenAuthentication,)

	def get_queryset(self):
		report = CourseReport.objects.get(pk=self.kwargs['pk'])
		course = report.course
		qs = course.missingassignment_set.all()
		return qs

class UpdateMissingWorkView(UpdateAPIView):
	model = MissingAssignment
	serializer_class = MissingAssignmentSerializer
	authentication_class = (authentication.TokenAuthentication,)
	queryset = MissingAssignment.objects.all()

class DestroyMissingWorkView(DestroyAPIView):
	model = MissingAssignment
	serializer_class = CourseMissingAssignmentSerializer
	authentication_class = (authentication.TokenAuthentication,)
	queryset = MissingAssignment.objects.all()

class CreateMissingWorkView(CreateAPIView):
	model = MissingAssignment
	serializer_class = MissingAssignmentSerializer
	authentication_class = (authentication.TokenAuthentication,)

class MissingWorkStudentsView(View):
	http_method_names = [u'get',u'put']

	@method_decorator(json_view)
	@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return super(MissingWorkStudentsView, self).dispatch(request,*args,**kwargs)

	def get(self,request,*args,**kwargs):
		report = CourseReport.objects.get(pk=kwargs['report_id'])
		missing_assignment = MissingAssignment.objects.get(pk=kwargs['mw_id'])
		all_students = []
		for d in report.deposit_set.all().order_by('student__last_name'):
			all_students.append(d.student)
		students_missing_work = missing_assignment.students.all()
		students_not_missing_work = []
		for s in all_students:
			if s not in students_missing_work:
				students_not_missing_work.append(s)
		assignment_serializer = MissingAssignmentSerializer(missing_assignment)
		students_missing_work_serializer = BasicStudentSerializer(students_missing_work,many=True)
		students_not_missing_work_serializer = BasicStudentSerializer(students_not_missing_work,many=True)
		response = {
			'assignment':assignment_serializer.data,
			'missing':students_missing_work_serializer.data,
			'notMissing':students_not_missing_work_serializer.data,
		}
		return response

	def put(self,request,*args,**kwargs):
		stream = BytesIO(request.body)
		data = JSONParser().parse(stream)
		missing = data['missing']
		not_missing = data['notMissing']
		assignment = MissingAssignment.objects.get(pk=data['assignment'])
		for s in missing:
			student = Student.objects.get(pk=s['id'])
			if student not in assignment.students.all():
				assignment.students.add(student)
		for s in not_missing:
			student = Student.objects.get(pk=s['id'])
			if student in assignment.students.all():
				assignment.students.remove(student)
		return MissingAssignmentSerializer(assignment).data

class IsMenteeView(View):
	http_method_names = [u'get']

	@method_decorator(json_view)
	@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return super(IsMenteeView,self).dispatch(request,*args,**kwargs)

	def get(self,request,*args,**kwargs):
		teacher_id = kwargs.pop('teacher_id')
		student_id = kwargs.pop('student_id')
		teacher = UserProfile.objects.get(pk=teacher_id)
		student = Student.objects.get(pk=student_id)
		pot_courses = student.course_set.filter(hour='Mentoring')
		for c in pot_courses:
			if teacher in c.teachers.all():
				return {'mentee':True}
		return {'mentee':False}

class SearchStudentsView(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		students = Student.objects.filter(active=True)
		if data['grade']:
			students = students.filter(grade=data['grade'])
		return Response(BasicStudentSerializer(students,many=True).data)

class MenteeListView(ListAPIView):
	model = Student
	serializer_class = BasicStudentSerializer
	authentication_class = (authentication.TokenAuthentication,)

	def get_queryset(self):
		teacher = UserProfile.objects.get(pk=self.kwargs['pk'])
		today = datetime.date.today()
		students = []
		courses = teacher.course_set.filter(hour="Mentoring")
		for c in courses:
			for s in c.students.all():
				if s not in students:
					students.append(s)
		return students

class RetrieveStudentsEligibleToPurchase(ListAPIView):
	model = Student
	serializer_class = BasicStudentSerializer
	authentication_class = (authentication.TokenAuthentication,)

	def get_queryset(self):
		course = Course.objects.get(pk=self.kwargs['pk'])
		report = CourseReport.objects.filter(course=course).last()
		students = []
		deposits = report.deposit_set.all()
		for d in deposits:
			if len(d.student.missingassignment_set.all()) == 0:
				students.append(d.student)
		return students

class RetrieveStudentsIneligibleToPurchase(ListAPIView):
	model = Student
	serializer_class = BasicStudentSerializer
	authentication_class = (authentication.TokenAuthentication,)

	def get_queryset(self):
		course = Course.objects.get(pk=self.kwargs['pk'])
		report = CourseReport.objects.filter(course=course).last()
		students = []
		deposits= report.deposit_set.all()
		for d in deposits:
			if len(d.student.missingassignment_set.all()) > 0:
				students.append(d.student)
		return students

class RetrieveStudentsNotMissingWork(ListAPIView):
	model = Student
	serializer_class = BasicStudentSerializer
	authentication_class = (authentication.TokenAuthentication,)

	def get_queryset(self):
		report = CourseReport.objects.get(pk=self.kwargs['report_id'])
		all_students = []
		for d in report.deposit_set.all():
			all_students.append(d.student)
		students_missing_work = MissingAssignment.objects.get(pk=self.kwargs['assignment_id']).students.all()
		students_not_missing_work = []
		for s in all_students:
			if s not in students_missing_work:
				students_not_missing_work.append(s)
		return students_not_missing_work

class RetrieveStudentMissingWorkView(ListAPIView):
	model = MissingAssignment
	serializer_class = CourseMissingAssignmentSerializer
	authentication_class = (authentication.TokenAuthentication,)

	def get_queryset(self):
		student = Student.objects.get(pk=self.kwargs['pk'])
		qs = student.missingassignment_set.all()
		return qs

class RetrieveStudentView(RetrieveAPIView):
	model = Student
	serializer_class = BasicStudentSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	queryset = Student.objects.all()

class RetrievePersonalBehaviorGoalsView(ListAPIView):
	model = PersonalBehaviorGoal
	serializer_class = StudentPersonalBehaviorGoalSerializer
	authentication_classes = (authentication.TokenAuthentication,)

	def get_queryset(self):
		student = Student.objects.get(pk=self.kwargs['pk'])
		qs = student.personalbehaviorgoal_set.filter(active=True)
		return qs

class RetrieveRecentDepositsView(ListAPIView):
	model = Deposit
	serializer_class = StudentDepositSerializer
	authentication_classes = (authentication.TokenAuthentication,)

	def get_queryset(self):
		two_weeks_ago = datetime.date.today() - datetime.timedelta(days=14)
		student = Student.objects.get(pk=self.kwargs['pk'])
		qs = Deposit.objects.filter(student=student,course_report__completed=True,transaction_ptr__date__gte=two_weeks_ago)
		return qs

class RetrieveStudentDailyDeposits(ListAPIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		student_id = data['student_id']
		student = Student.objects.get(pk=student_id)
		date = data.pop('date',False)
		if not date:
			date = datetime.date.today()
		qs = Deposit.objects.filter(student=student,course_report__completed=True,transaction_ptr__date=date)
		return qs

class RetrieveRecentNotesView(ListAPIView):
	model = Deposit
	serializer_class = DepositNotesSerializer
	authentication_classes = (authentication.TokenAuthentication,)

	def dispatch(self,request,*args,**kwargs):
		self.student_id = kwargs.pop('student_id')
		super(RetrieveRecentNotesView,self).dispatch(*args,**kwargs)

	def get_queryset(self):
		today = datetime.date.today()
		weekday = today.weekday()
		monday = today - datetime.timedelta(days=weekday)
		last_monday = monday - datetime.timedelat(days=7)
		student_id = self.student_id
		student = Student.objects.get(pk=student_id)
		deposits = Deposit.objects.filter(
			student=student,
			course_report__completed=True,
			note__isnull=False,
			date__gte=last_monday,
		).exclude(
			note=""
		)
		return deposits

class RetrieveRecentTTwoReportsView(ListAPIView):
	model = TTwoReport
	serializer_class = TTwoReportSerializer
	authentication_classes = (authentication.TokenAuthentication,)

	def get_queryset(self):
		two_weeks_ago = datetime.date.today() - datetime.timedelta(days=14)
		student = Student.objects.get(pk=self.kwargs['pk'])
		profile = student.ttwoprofile_set.first()
		qs = TTwoReport.objects.filter(report__date__gte=two_weeks_ago,goal__profile=profile)
		return qs

class RetrieveTierThreeChartView(View):
	http_method_names=[u'post']

	@method_decorator(json_view)
	@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return super(RetrieveTierThreeChartView,self).dispatch(request,*args,**kwargs)

	def post(self,request,*args,**kwargs):
		stream = BytesIO(request.body)
		data = JSONParser().parse(stream)
		student_id = data['student_id']
		student = Student.objects.get(pk=student_id)
		raw_date = data.pop('date',False)
		if not raw_date:
			date = datetime.date.today()
		else:
			year, month, day = raw_date.split('-')
			date = datetime.date(int(year),int(month),int(day))
		init_weekday = date.weekday()
		monday = date - datetime.timedelta(days=init_weekday)
		friday = monday + datetime.timedelta(days=4)
		if not student.is_tthree:
			return []
		profile = student.tthreeprofile_set.first()
		goals = profile.tthreegoal_set.all()
		response = {
			'goals': TThreeGoalSerializer(goals,many=True).data,
		}

		def get_chart(profile,start,end):
			response = {}
			response['courses'] = []
			day_two = start + datetime.timedelta(days=1)
			day_three = start + datetime.timedelta(days=2)
			day_four = start + datetime.timedelta(days=3)
			response['col_headers']=[
				"Course",
				start.strftime("%m/%d/%y"),
				day_two.strftime("%m/%d/%y"),
				day_three.strftime("%m/%d/%y"),
				day_four.strftime("%m/%d/%y"),
				end.strftime("%m/%d/%y"),
				"Blues and Greens"
			]
			reports = profile.tthreereport_set.filter(report__date__gte=start,report__date__lte=end,report__completed=True,absent=False,iss=False).order_by('report__start_time')
			course_list = []
			for r in reports:
				if r.report.course.name not in course_list:
					course_list.append(r.report.course.name)
			for c in course_list:
				course_data = {
					'course':c,
					'scores':[0,0,0,0,0],
					'summary':0,
					'num':0,
				}
				course_reports = reports.filter(report__course__name=c).order_by('report__date')
				for cr in course_reports:
					course_data['scores'][cr.report.date.weekday()]=cr.score
					course_data['num'] += 1
					if cr.score > 2:
						course_data['summary'] += 1
				for i, item in enumerate(course_data['scores']):
					if item == 0:
						course_data['scores'][i] = "-"
				response['courses'].append(course_data)
			response['totals'] = {
				'scores':[0,0,0,0,0],
				'summary':0,
				'num':0
			}
			total = 0
			num = 0
			for d in [0,1,2,3,4]:
				daily_total = 0
				daily_num = 0
				for course in response['courses']:
					if course['scores'][d] != "-":
						num += 1
						daily_num += 1
						if course['scores'][d] > 2:
							total += 1
							daily_total += 1
				if daily_num != 0:
					response['totals']['scores'][d] = str("%.2f" % round(float(daily_total)/float(daily_num)*100,2)) + "%"
				else:
					response['totals']['scores'][d] = "-"


			if num != 0:
				response['totals']['summary'] = str("%.2f" % round(float(total)/float(num)*100,2)) + "%"
			else:
				response['totals']['summary'] = '-'

			return response

		response['chart'] = get_chart(profile,monday,friday)

		return response

class RetrieveTierTwoChartView(View):
	http_method_names=[u'post']

	@method_decorator(json_view)
	@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return super(RetrieveTierTwoChartView,self).dispatch(request,*args,**kwargs)

	def post(self,request,*args,**kwargs):
		stream = BytesIO(request.body)
		data = JSONParser().parse(stream)
		student_id = data['student_id']
		student = Student.objects.get(pk=student_id)
		raw_date = data.pop('date',False)
		if not raw_date:
			date = datetime.date.today()
		else:
			year, month, day = raw_date.split('-')
			date = datetime.date(int(year),int(month),int(day))
		init_weekday = date.weekday()
		monday = date - datetime.timedelta(days=init_weekday)
		friday = monday + datetime.timedelta(days=4)
		if not student.is_ttwo:
			return []
		profile = student.ttwoprofile_set.first()
		goals = profile.ttwogoal_set.all()
		response = []

		def get_goal_scores(goal,start,end):
			response = {}
			response['goal'] = TTwoGoalSerializer(goal).data
			response['courses'] = []
			day_two = start + datetime.timedelta(days=1)
			day_three = start + datetime.timedelta(days=2)
			day_four = start + datetime.timedelta(days=3)
			response['col_headers'] = ["Course",start.strftime("%m/%d/%y"),day_two.strftime("%m/%d/%y"),day_three.strftime("%m/%d/%y"),day_four.strftime("%m/%d/%y"),end.strftime("%m/%d/%y")]
			reports = goal.ttworeport_set.filter(report__date__gte=start,report__date__lte=end,report__completed=True,absent=False,iss=False).order_by('report__start_time')
			course_list = []
			for r in reports:
				if r.report.course.name not in course_list:
					course_list.append(r.report.course.name)
			for c in course_list:
				course_data = {
					'course':c,
					'scores':[0,0,0,0,0],
					'summary':0,
					'num':0,
				}
				course_reports = reports.filter(report__course__name=c).order_by('report__date')
				for cr in course_reports:
					course_data['scores'][cr.report.date.weekday()] = cr.score
					course_data['num'] += 1
					if cr.score > 2:
						course_data['summary'] += 1
				for i,item in enumerate(course_data['scores']):
					if item == 0:
						course_data['scores'][i] = "-"
				response['courses'].append(course_data)

			response['totals'] = {
				'scores':[0,0,0,0,0],
				'summary':0
			}
			total = 0
			num = 0
			for d in [0,1,2,3,4]:
				daily_total = 0
				daily_num = 0
				for course in response['courses']:
					if course['scores'][d] != "-":
						num += 1
						daily_num += 1
						if course['scores'][d] > 2:
							total += 1
							daily_total += 1
				if daily_num != 0:
					response['totals']['scores'][d] = str("%.2f" % round(float(daily_total)/float(daily_num)*100,2)) + "%"
				else:
					response['totals']['scores'][d] = '-'

			if num != 0:
				response['totals']['summary'] = str("%.2f" % round(float(total)/float(num)*100,2)) + "%"
			else:
				response['totals']['summary'] = '-'

			return response


		for g in goals:
			goal_scores = get_goal_scores(g,monday,friday)
			if len(goal_scores['courses']) > 0:
				response.append(goal_scores)

		return response

class RetrieveTierThreeNotesView(View):
	http_method_names=[u'post']

	@method_decorator(json_view)
	@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return super(RetrieveTierThreeNotesView,self).dispatch(request,*args,**kwargs)

	def post(self,request,*args,**kwargs):
		stream = BytesIO(request.body)
		data = JSONParser().parse(stream)
		student_id = data.pop('student_id')
		student = Student.objects.get(pk=student_id)
		raw_date = data.pop('date',False)
		if not raw_date:
			date = datetime.date.today()
		else:
			year, month, day = raw_date.split('-')
			date = datetime.date(int(year),int(month),int(day))
		init_weekday = date.weekday()
		monday = date - datetime.timedelta(days=init_weekday)
		friday = monday + datetime.timedelta(days=4)
		if not student.is_tthree():
			return []
		profile = student.tthreeprofile_set.first()
		reports = profile.tthreereport_set.filter(
			report__date__gte=monday,
			report__date__lte=friday,
			report__completed=True
		).exclude(
			note__isnull=True
		).exclude(
			note__exact=""
		).order_by('report__date','report__end_time')
		print "-----------------------"
		print reports
		serializer = TThreeReportSerializer(reports,many=True)
		print serializer
		print serializer.data
		return serializer.data

class RetrieveTierTwoNotesView(View):
	http_method_names=[u'post']

	@method_decorator(json_view)
	@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return super(RetrieveTierTwoNotesView,self).dispatch(request,*args,**kwargs)

	def post(self,request,*args,**kwargs):
		stream = BytesIO(request.body)
		data = JSONParser().parse(stream)
		student_id = data.pop('student_id')
		student = Student.objects.get(pk=student_id)
		raw_date = data.pop('date',False)
		if not raw_date:
			date = datetime.date.today()
		else:
			year, month, day = raw_date.split('-')
			date = datetime.date(int(year),int(month),int(day))
		init_weekday = date.weekday()
		monday = date - datetime.timedelta(days=init_weekday)
		friday = monday + datetime.timedelta(days=4)
		if not student.is_ttwo():
			return []
		profile = student.ttwoprofile_set.first()
		reports = TTwoReport.objects.filter(
			goal__profile=profile,
			report__date__gte=monday,
			report__date__lte=friday,
			report__completed=True
			).exclude(
			note__isnull=True
			).exclude(
			note__exact=""
			).order_by(
			'report__date',
			'report__end_time'
			)
		serializer = TTwoReportSerializer(reports,many=True)
		return serializer.data

class RetrieveRecentTThreeReportsView(ListAPIView):
	model = TThreeReport
	serializer_class = TThreeReportSerializer
	authentication_classes = (authentication.TokenAuthentication,)

	def get_queryset(self):
		two_weeks_ago = datetime.date.today() - datetime.timedelta(days=14)
		student = Student.objects.get(pk=self.kwargs['pk'])
		if student.tthreeprofile_set.exists():
			profile = student.tthreeprofile_set.first()
			try:
				qs = profile.tthreereport_set.filter(report__date__gte=two_weeks_ago, report__completed=True)
				return qs
			except:
				return False
		else:
			return False

class RetrieveStudentScheduleView(ListAPIView):
	model = CourseReport
	serializer_class = CourseReportSerializer
	authentication_classes = (authentication.TokenAuthentication,)

	def get_queryset(self):
		date = datetime.date.today()
		student = Student.objects.get(pk=self.kwargs['pk'])
		qs = []
		while len(qs) == 0:
			date = date - datetime.timedelta(days=1)
			qs = CourseReport.objects.filter(deposit__student=student,date=date)
			if date < (date - datetime.timedelta(days=14)):
				return qs
		return qs

class RetrieveStudentDailyScheduleView(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		student_id = data['student_id']
		student = Student.objects.get(pk=student_id)
		date = data.pop('date',False)
		if !date:
			date = datetime.date.today()
		schedule = DailySchedule.objects.filter(date=date).first().schedule
		if !schedule:
			return Response({'error':'There are no courses scheduled for today'})
		schedule = []
		for ts in schedule.time_slots.filter(grade=student.grade):
			reports = CourseReport.objects.filter(hour=ts.hour,course__students=student)
			block = {
				'hour':ts.hour,
				'start_time':ts.start_time,
				'end_time':ts.end_time,
				'courses':CourseReportSerializer(reports,many=True).data
			}
			schedule.append(block)
		return Response(schedule)

class RetrieveStudentStatisticsView(View):
	http_method_names = [u'get']

	@method_decorator(json_view)
	@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return super(RetrieveStudentStatisticsView, self).dispatch(request,*args,**kwargs)

	def get(self,request,*args,**kwargs):
		response = {
			'bucks_by_goal':{},
			'bucks_by_course':{},
		}
		student_id = kwargs.pop('pk')
		student = Student.objects.get(pk=student_id)
		two_weeks_ago = datetime.date.today() - datetime.timedelta(days=14)
		bucks = Buck.objects.filter(deposit__student=student,deposit__date__gte=two_weeks_ago,deposit__course_report__completed=True)
		goals = BehaviorGoal.objects.filter(active=True)
		for g in goals:
			stats = {
				'name': g.goal,
				'earned':len(bucks.filter(goal=g,earned=True)),
				'unearned':len(bucks.filter(goal=g,earned=False)),
			}
			response['bucks_by_goal'][g.pk]=stats
		for b in bucks:
			if not response['bucks_by_course'].has_key(b.deposit.course_report.course.pk):
				response['bucks_by_course'][b.deposit.course_report.course.pk] = {
					'name':'',
					'earned':0,
					'unearned':0,
				}
				response['bucks_by_course'][b.deposit.course_report.course.pk]['name'] = b.deposit.course_report.course.name
			if b.earned:
				response["bucks_by_course"][b.deposit.course_report.course.pk]['earned'] += 1
			else:
				response['bucks_by_course'][b.deposit.course_report.course.pk]['unearned'] += 1

		return response

class RetrieveStudentAbsencesView(ListAPIView):
	model = Absence
	serializer_class = AbsenceSerializer
	authentication_classes = (authentication.TokenAuthentication,)

	def dispatch(self,request,*args,**kwargs):
		self.student_id = kwargs.pop('student_id')
		super (RetrieveStudentAbsencesView,self).dispatch(*args,**kwargs)

	def get_queryset(self):
		last_monday = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday()+7)
		student_id = self.kwargs.pop('student_id')
		student = Student.objects.get(pk=student_id)
		absences = Absence.objects.filter(student=student,date__gte=last_monday)
		return absences

##Schedule Serializers
class TimeSlotViewSet(viewsets.ModelViewSet):
	queryset = TimeSlot.objects.all()
	serializer_class = TimeSlotSerializer
	authentication_classes = (authentication.TokenAuthentication,)

class ScheduleViewSet(viewsets.ModelViewSet):
	queryset = Schedule.objects.all()
	serializer_class = ScheduleSerializer
	authentication_classes = (authentication.TokenAuthentication,)

class DailyScheduleViewSet(viewsets.ModelViewSet):
	queryset = DailySchedule.objects.all()
	serializer_class = DailyScheduleSerializer
	authentication_classes = (authentication.TokenAuthentication,)

class GetScheduleByDateView(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def post(self,request,*args,**kwargs):
		data = request.data
		year = int(data['date']['year'])
		month = int(data['date']['month'])
		day = int(data['date']['day'])
		date = datetime.date(year,month,day)
		daily_schedule = DailySchedule.objects.filter(date=date).first()
		return Response(DailyScheduleSerializer(daily_schedule).data)
