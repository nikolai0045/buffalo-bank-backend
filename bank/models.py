# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

USER_TYPE_CHOICES = [
	('ADMIN','ADMIN'),
	('TEACHER','TEACHER'),
	('OBSERVER','OBSERVER')
]
class Student(models.Model):
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	grade = models.CharField(max_length=3)
	active = models.BooleanField(default=True)
	external_id = models.CharField(max_length=255)
	account_balance = models.IntegerField(default=0)

	def __str__(self):
		return self.first_name + " " + self.last_name

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	user_type = models.CharField(max_length=20,choices=USER_TYPE_CHOICES,default='TEACHER')
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	email = models.EmailField()

	def __str__(self):
		return self.first_name + " " + self.last_name

class Course(models.Model):
	name = models.CharField(max_length=255)
	course_number = models.CharField(max_length=255)
	section_number = models.CharField(max_length=255)
	external_id = models.CharField(max_length=255)
	students = models.ManyToManyField(Student)
	teachers = models.ManyToManyField(UserProfile)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.name + " - Section #" + self.section_number

class BehaviorGoal(models.Model):
	goal = models.CharField(max_length=255)
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.goal

class Transaction(models.Model):
	student = models.ForeignKey(Student)
	datetime = models.DateTimeField(auto_now=True)

class CourseReport(models.Model):
	course = models.ForeignKey(Course)
	date = models.DateField()
	start_time = models.TimeField()
	end_time = models.TimeField()
	completed = models.BooleanField(default=False)

	def __str__(self):
		return str(self.course.name) + " - " + str(self.date)

class Deposit(Transaction):
	course_report = models.ForeignKey(CourseReport)
	##consider refactoring this as a function
	amount_earned = models.IntegerField(default=0)

	def __str__(self):
		return str(self.student) + " - " + self.course_report.course.name + " " + str(self.datetime)

	##def amount_earned(self):
	##	return len(self.buck_set.filter(earned=True))

class PurchaseItem(models.Model):
	name = models.CharField(max_length=255)
	current_price = models.IntegerField(default=0)
	quantity_remaining = models.IntegerField(default=0)
	image = models.FileField()

	def __str__(self):
		return self.name + " - $" + self.current_price

class Purchase(Transaction):
	item = models.ForeignKey(PurchaseItem)
	price = models.IntegerField(default=0)

	def __str__(self):
		return str(self.student) + " - " + self.item.name + " - $" + str(self.price)

class Buck(models.Model):
	deposit = models.ForeignKey(Deposit)
	goal = models.ForeignKey(BehaviorGoal)
	earned = models.BooleanField(default=True)

	def __str__(self):
		return str(self.deposit.student) + " - " + str(self.goal)
