# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from bank.models import Student, CourseReport, UserProfile

class TThreeProfile(models.Model):
	student = models.ForeignKey(Student)
	active = models.BooleanField(default=True)
	mentor = models.ForeignKey(UserProfile)

class TThreeGoal(models.Model):
	profile = models.ForeignKey(TThreeProfile)
	active = models.BooleanField(default=True)
	goal = models.CharField(max_length=255)

class TThreeReport(models.Model):
	profile = models.ForeignKey(TThreeProfile)
	report = models.ForeignKey(CourseReport)
	score = models.IntegerField(default=4)
