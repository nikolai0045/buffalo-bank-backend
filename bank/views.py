# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework import status, authentication, permissions

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
)
from tier_two.models import TTwoReport
from tier_three.models import TThreeReport

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

class RetrieveBehaviorGoalsView(ListAPIView):
    model = BehaviorGoal
    serializer_class = BehaviorGoalSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    queryset = BehaviorGoal.objects.filter(active=True)
	
class RetrieveStudentMissingWorkView(ListAPIView):
	model = MissingAssignment
	serializer_class = MissingAssignmentSerializer
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
	
class RetrieveRecentTTwoReportsView(ListAPIView):
	model = TTwoReport
	serializer_class = TTwoReportSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get_queryset(self):
		two_weeks_ago = datetime.date.today() - datetime.timedelta(days=14)
		student = Student.objects.get(pk=self.kwargs['pk'])
		profile = student.ttwoprofile_set.first()
		if profile.exists():
			qs = TTwoReport.objects.filter(date__gte=two_weeks_ago,goal__profile=profile)
			return qs
		else:
			return {[]}
		
class RetrieveRecentTThreeReportsView(ListAPIView):
	model = TThreeReport
	serializer_class = TThreeReportSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get_queryset(self):
		two_weeks_ago = datetime.date.today() - datetime.timdelta(days=14)
		student = Student.objects.get(pk=self.kwargs['pk'])
		profile = student.tthreeprofile_set.first()
		if profile.exists():
			qs = profile.tthreereport_set.filter(date__gte=two_weeks_ago)
			return qs
		else:
			return {[]}
		
class RetrieveStudentScheduleView(ListAPIView):
	model = CourseReport
	serializer_class = CourseReportSerializer
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get_queryset(self):
		date = datetime.date.today()
		student = Student.objects.get(pk=self.kwargs['pk'])
		qs = []
		while len(qs) == 0:
			qs = CourseReport.objects.filter(deposit__student=student)
			date = date - datetime.timedelta(days=1)
			if date < (date - datetime.timedelta(days=14)):
				return qs
		return qs
	
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
			response['bucks_by_goal'][g.goal] = []
			response['bucks_by_goal'][g.goal].append(len(bucks.filter(goal=g,earned=True)))
			response['bucks_by_goal'][g.goal].append(len(bucks.filter(goal=g,earned=False)))
		for b in bucks:
			if not response['bucks_by_course'].has_key(b.deposit.course_report.course.name):
				response['bucks_by_course'][b.deposit.course_report.course.name] = [0,0]
			if b.earned:
				response["bucks_by_course"][b.deposit.course_report.course.name][0] += 1
			else:
				response['bucks_by_course'][b.deposit.course_report.course.name][1] += 1
				
		return response
		

	
			