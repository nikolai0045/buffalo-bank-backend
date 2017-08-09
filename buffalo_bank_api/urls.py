"""buffalo_bank_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from accounts.views import SendEmailInvites, VerifyInvitationKey, CreateUserView, RetrieveUserView
from bank.views import (
	RetrieveReportsView,
	RetrieveActiveCoursesView,
	RetrieveStudentsByCourseView,
	RetrieveCourseReportView,
	RetrieveBehaviorGoalsView,
	UpdateCourseReportView,
	RetrieveStudentMissingWorkView,
	RetrievePersonalBehaviorGoalsView,
	RetrieveRecentDepositsView,
	RetrieveRecentTTwoReportsView,
	RetrieveRecentTThreeReportsView,
	RetrieveStudentView,
	RetrieveStudentScheduleView,
	RetrieveStudentStatisticsView,
    UpdatePersonalBehaviorGoalView,
    CreatePersonalBehaviorGoalView,
    RetrieveCourseMissingWorkView,
    RetrieveStudentsNotMissingWork,
    UpdateMissingWorkView,
    DestroyMissingWorkView,
    CreateMissingWorkView,
	)
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
	url(r'^admin/', admin.site.urls),
	# url(r'^rest-auth/password/reset/$', PasswordResetView.as_view(), name='rest_password_reset'),
	url(r'^rest-auth/registration/',include('rest_auth.registration.urls')),
	url(r'^rest-auth/',include('rest_auth.urls')),
	url(r'^accounts/send_invites/$',SendEmailInvites.as_view()),
	url(r'^accounts/verify_key/(?P<key>\w+)/$',VerifyInvitationKey.as_view()),
	url(r'^accounts/create_user/(?P<key>\w+)/$',CreateUserView.as_view()),
	url(r'^bank/current_user/$',RetrieveUserView.as_view()),
	url(r'^bank/user/(?P<uid>[0-9]+)/$',RetrieveUserView.as_view()),
	url(r'^bank/reports/$',RetrieveReportsView.as_view()),
	url(r'^bank/reports/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/$',RetrieveReportsView.as_view()),
	url(r'^bank/courses/active/$',RetrieveActiveCoursesView.as_view()),
    url(r'^bank/courses/missing_work/(?P<pk>[0-9]+)/$',RetrieveCourseMissingWorkView.as_view()),
    url(r'^bank/courses/not_missing_work/(?P<report_id>[0-9]+)/(?P<assignment_id>[0-9]+)/$',RetrieveStudentsNotMissingWork.as_view()),
    url(r'^bank/courses/missing_work/update/(?P<pk>[0-9]+)/$',UpdateMissingWorkView.as_view()),
    url(r'^bank/courses/missing_work/destroy/(?P<pk>[0-9]+)/$',DestroyMissingWorkView.as_view()),
    url(r'^bank/courses/missing_work/create/$',CreateMissingWorkView.as_view()),
	url(r'^bank/roster/(?P<pk>[0-9]+)/$',RetrieveStudentsByCourseView.as_view()),
	url(r'^bank/course_report/(?P<pk>[0-9]+)/$',RetrieveCourseReportView.as_view()),
	url(r'^bank/course_report/save/(?P<pk>[0-9]+)/$', UpdateCourseReportView.as_view()),
	url(r'^bank/behavior_goals/active/$',RetrieveBehaviorGoalsView.as_view()),
	url(r'^bank/student/(?P<pk>[0-9]+)/$',RetrieveStudentView.as_view()),
	url(r'^bank/student/(?P<pk>[0-9]+)/missing_assignments/$',RetrieveStudentMissingWorkView.as_view()),
	url(r'^bank/student/goals/(?P<pk>[0-9]+)/$',RetrievePersonalBehaviorGoalsView.as_view()),
	url(r'^bank/student/recent_deposits/(?P<pk>[0-9]+)/$',RetrieveRecentDepositsView.as_view()),
	url(r'^bank/student/recent_ttwo_reports/(?P<pk>[0-9]+)/$',RetrieveRecentTTwoReportsView.as_view()),
	url(r'^bank/student/recent_tthree_reports/(?P<pk>[0-9]+)/$',RetrieveRecentTThreeReportsView.as_view()),
	url(r'^bank/student/schedule/(?P<pk>[0-9]+)/$',RetrieveStudentScheduleView.as_view()),
	url(r'^bank/student/statistics/(?P<pk>[0-9]+)/$',RetrieveStudentStatisticsView.as_view()),
    url(r'^bank/student/update_goal/(?P<pk>[0-9]+)/$',UpdatePersonalBehaviorGoalView.as_view()),
    url(r'^bank/student/new_goal/$',CreatePersonalBehaviorGoalView.as_view()),
	url(r'^get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
]
