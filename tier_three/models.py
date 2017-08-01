# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from bank.models import Student, CourseReport, UserProfile

class T3Profile(models.Model):
	student = models.ForeignKey(Student)
	active = models.BooleanField(default=True)
	mentor = models.ForeignKey(UserProfile)

class T3Goal(models.Model):
	profile = models.ForeignKey(T3Profile)
	active = models.BooleanField(default=True)
	goal = models.CharField(max_length=255)

class T3Report(models.Model):
	profile = models.ForeignKey(T3Profile)
	report = models.ForeignKey(CourseReport)
	score = models.IntegerField(default=4)
