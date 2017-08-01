# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from smtplib import SMTPRecipientsRefused

from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.core.validators import validate_email


from jsonview.decorators import json_view

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, authentication, permissions

from .forms import CleanEmailMixin
from .models import Invitation
from .exceptions import AlreadyInvited, AlreadyAccepted, UserRegisteredEmail
from .serializers import EmailInvitationSerializer

from bank.models import UserProfile
from bank.serializers import UserProfileSerializer

class SendEmailInvites(View):
	http_method_names = [u'post']

	@method_decorator(json_view)
	@method_decorator(csrf_exempt)
	def dispatch(self,request,*args,**kwargs):
		return super(SendEmailInvites, self).dispatch(request,*args,**kwargs)

	def post(self,request,*args,**kwargs):
		status_code = 400
		invitees = json.loads(request.body.decode())
		response = {'valid':[],'invalid':[]}
		if isinstance(invitees, list):
			for invitee in invitees:
				try:
					print invitee
					serializer = EmailInvitationSerializer(data={'email':invitee})
					serializer.is_valid()
					# validate_email(invitee)
					# CleanEmailMixin().validate_invitation(invitee)
					# invite = Invitation.create(invitee)
				except(ValueError, KeyError):
					pass
				except(ValidationError):
					response['invalid'].append({invitee:'invalid email'})
				except(AlreadyAccepted):
					response['invalid'].append({invitee:'already accepted'})
				except(AlreadyInvited):
					response['invalid'].append({invitee:'pending invite'})
				except(UserRegisteredEmail):
					response['invalid'].append({invitee:'user registered email'})
				else:
					try:
						serializer.save(request)
					except(SMTPRecipientsRefused):
						response['invalid'].append({invitee:'not a valid email address'})
					else:
						response['valid'].append({invitee:'invited'})

			if response['valid']:
				status_code = 201

			return response

class VerifyInvitationKey(View):
	http_method_names = [u'get']

	@method_decorator(json_view)
	def dispatch(self,request,*args,**kwargs):
		return super(VerifyInvitationKey, self).dispatch(request,*args,**kwargs)

	def get(self,request,*args,**kwargs):
		key = kwargs.pop('key',False)
		if not key:
			return {'status':'failure','error':'Missing invitation key'}

		try:
			invitation = Invitation.objects.get(key=key)
		except Invitation.DoesNotExist:
			return {'status':'failure','error':'Invitation was not found'}

		if invitation.key_expired():
			return {'status':'failure','error':'Invitation has expired'}

		return {'status':'success','email':invitation.email}

class CreateUserView(View):
	http_method_names = [u'post']

	@method_decorator(csrf_exempt)
	@method_decorator(json_view)
	def dispatch(self,request,*args,**kwargs):
		return super(CreateUserView, self).dispatch(request,*args,**kwargs)

	def post(self,request,*args,**kwargs):
		data = json.loads(request.body.decode())
		key = kwargs.pop('key',False)
		if not key:
			return {'status':'failure','errors':['Missing invitation key']}

		errors = []
		if isinstance(data, dict):
			email = data.pop('email',False)
			if not email:
				errors.append('Missing email')

			username = data.pop('username',False)
			if not username:
				errors.append('Missing username')

			password = data.pop('password',False)
			if not password:
				errors.append('Missing password')

			first_name = data.pop('first_name',False)
			if not first_name:
				errors.append('Missing first name')

			last_name = data.pop('last_name',False)
			if not last_name:
				errors.append('Missing last name')

			if len(errors) > 0:
				return {'status':'failure','errors':errors}

		else:
			return {'status':'failure','errors':['Unknown error']}

		try:
			invitation = Invitation.objects.get(key=key)
		except Invitation.DoesNotExist:
			return {'status':'failure','errors':['Invitation not found']}

		if invitation.email != email:
			return {'status':'failure','errors':['Email address does not match invitation']}

		try:
			user = User.objects.get(username=username)
			return {'status':'failure','errors':['User with that username already exists']}
		except User.DoesNotExist:
			pass

		try:
			user = User.objects.get(email=email)
			return {'status':'failure','errors':['User with that email address already exists']}
		except User.DoesNotExist:
			pass

		new_user = User.objects.create_user(username=username,email=email,password=password)
		new_user.first_name = first_name
		new_user.last_name = last_name
		new_user.save()

		new_user_profile = UserProfile(user=new_user,email=email,first_name=first_name,last_name=last_name)
		new_user_profile.save()

		serializer = UserSerializer(new_user_profile)

		return {'status':'success','profile':serializer.data}

class RetrieveUserView(APIView):
	authentication_classes = (authentication.TokenAuthentication,)

	def get(self,request,format=None):
		user_id = self.kwargs.pop('uid',False)
		if not user_id:
			profile = UserProfile.objects.get(user=request.user)
		else:
			profile = UserProfile.objects.get(user__pk=user_id)

		serializer = UserProfileSerializer(instance=profile)
		return Response(serializer.data)
