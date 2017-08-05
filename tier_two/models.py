# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from bank.models import Student, CourseReport, UserProfile

class TTwoProfile(models.Model):
	student = models.ForeignKey(Student)
	mentor = models.ForeignKey(UserProfile)
	active = models.BooleanField(default=True)

class TTwoGoal(models.Model):
	profile = models.ForeignKey(TTwoProfile)
	goal = models.CharField(max_length=255)
	active = models.BooleanField(default=False)

class TTwoReport(models.Model):
	goal = models.ForeignKey(TTwoGoal)
	report = models.ForeignKey(CourseReport)
	score = models.IntegerField(default=5)
