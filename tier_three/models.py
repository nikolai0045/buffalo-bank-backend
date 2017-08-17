# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from bank.models import Student, CourseReport, UserProfile

class TThreeProfile(models.Model):

	def __str__(self):
		return str(self.student) + " - PASS Profile"
	student = models.ForeignKey(Student)
	active = models.BooleanField(default=True)
	mentor = models.ForeignKey(UserProfile,blank=True,null=True)

class TThreeGoal(models.Model):
	profile = models.ForeignKey(TThreeProfile)
	active = models.BooleanField(default=True)
	goal = models.CharField(max_length=255)

	def __str__(self):
		return self.goal + str(self.profile)

class TThreeReport(models.Model):
	profile = models.ForeignKey(TThreeProfile)
	report = models.ForeignKey(CourseReport)
	score = models.IntegerField(default=4)
	note = models.TextField(null=True,blank=True)

	def __str__(self):
		return str(self.profile) + ' - ' + str(self.report)
