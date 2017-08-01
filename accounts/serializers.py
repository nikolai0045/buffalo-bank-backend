from django.contrib.auth.models import User

from rest_framework import serializers
from rest_auth.serializers import PasswordResetSerializer as BasePasswordResetSerializer

from .models import Invitation
from .exceptions import AlreadyInvited, AlreadyAccepted, UserRegisteredEmail


class PasswordResetSerializer(BasePasswordResetSerializer):

	def get_email_options(self):
		subject_template_name = 'accounts/email/password_reset_subject.txt'
		email_template_name = 'accounts/email/password_reset_message.txt'

		return {'subject_template_name':subject_template_name,'email_template_name':email_template_name}

class EmailInvitationSerializer(serializers.Serializer):
	email = serializers.EmailField()

	def validate_email(self,value):
		print 'validating email'
		if Invitation.objects.all_valid().filter(email__iexact=value, accepted=False):
			print "this person already invited"
			raise AlreadyInvited
		elif Invitation.objects.filter(email__iexact=value,accepted=True):
			print "this person already accepted"
			raise AlreadyAccepted
		elif User.objects.filter(email__iexact=value):
			print "this person already registered"
			raise UserRegisteredEmail
		else:
			return value

	def save(self, request):
		invite = Invitation.create(self.fields['email'])
		invite.send_invitation(request)


class SendEmailInvitationsSerializer(serializers.Serializer):
	invitees = EmailInvitationSerializer(many=True)

	def validate_invitee(self,value):
		if Invitation.objects.all_valid().filter(email__iexact=email, accepted=False):
			raise AlreadyInvited
		elif Invitation.objects.filter(email__iexact=email,accepted=True):
			raise AlreadyAccepted
		elif User.objects.filter(email__iexact=email):
			raise UserRegisteredEmail
		else:
			return True
