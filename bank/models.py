# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

USER_TYPE_CHOICES = [
	('ADMIN','ADMIN'),
	('TEACHER','TEACHER'),
	('OBSERVER','OBSERVER'),
	('MERCHANT','MERCHANT')
]
class Student(models.Model):
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	grade = models.CharField(max_length=3)
	active = models.BooleanField(default=True)
	external_id = models.CharField(max_length=255)
	account_balance = models.IntegerField(default=0)

	def is_ttwo(self):
		if self.ttwoprofile_set.filter(active=True).exists():
			return True
		return False

	def is_tthree(self):
		if self.tthreeprofile_set.filter(active=True).exists():
			return True
		return False

	def __str__(self):
		return self.first_name + " " + self.last_name

class PersonalBehaviorGoal(models.Model):
	student = models.ForeignKey(Student)
	active = models.BooleanField(default=True)
	name = models.CharField(max_length=200)
	description = models.TextField(null=True,blank=True)

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
	date = models.DateField()
	time = models.TimeField()

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
	note = models.TextField(blank=True,null=True)

	def __str__(self):
		return str(self.student) + " - " + self.course_report.course.name + " " + str(self.date)

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

class BehaviorNote(models.Model):
	student = models.ForeignKey(Student)
	report = models.ForeignKey(CourseReport)
	note = models.TextField()

class MissingAssignment(models.Model):
	name = models.CharField(max_length=30)
	description = models.CharField(max_length=400,blank=True,null=True)
	students = models.ManyToManyField(Student)
	course = models.ForeignKey(Course)
	date = models.DateField(auto_now_add=True)
