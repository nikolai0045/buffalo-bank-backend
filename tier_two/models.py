# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from bank.models import Student, CourseReport, UserProfile

class T2Profile(models.Model):
	student = models.ForeignKey(Student)
	mentor = models.ForeignKey(UserProfile)
	active = models.BooleanField(default=True)

class T2Goal(models.Model):
	profile = models.ForeignKey(T2Profile)
	goal = models.CharField(max_length=255)
	active = models.BooleanField(default=False)

class T2Report(models.Model):
	goal = models.ForeignKey(T2Goal)
	report = models.ForeignKey(CourseReport)
	score = models.IntegerField(default=5)