# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

admin.site.register(Student)
admin.site.register(UserProfile)
admin.site.register(Course)
admin.site.register(CourseReport)
admin.site.register(BehaviorGoal)
admin.site.register(Transaction)
admin.site.register(Deposit)
admin.site.register(PurchaseItem)
admin.site.register(Purchase)
admin.site.register(Buck)
admin.site.register(MissingAssignment)

# Register your models here.
