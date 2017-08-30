# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from bank.models import Student, CourseReport, UserProfile

class TTwoProfile(models.Model):
	student = models.ForeignKey(Student)
	mentor = models.ForeignKey(UserProfile)
	active = models.BooleanField(default=True)

	def __str__(self):
		return str(self.student) + ' - Check and Connect Profile'

class TTwoGoal(models.Model):
	profile = models.ForeignKey(TTwoProfile)
	goal = models.CharField(max_length=255)
	active = models.BooleanField(default=False)

	def __str__(self):
		return str(self.profile) + ' - ' + self.goal

class TTwoReport(models.Model):
	goal = models.ForeignKey(TTwoGoal)
	report = models.ForeignKey(CourseReport)
	score = models.IntegerField(default=0)
	note = models.TextField(null=True,blank=True)
	absent = models.BooleanField(default=False)
	iss = models.BooleanField(default=False)
	not_applicable = models.BooleanField(default=False)

	def __str__(self):
		return str(self.goal) + ' - ' + str(self.report.course) + ' - ' + str(self.report.date)
