from django.contrib.auth.models import User

from .models import Invitation
from .exceptions import AlreadyInvited, AlreadyAccepted, UserRegisteredEmail

class CleanEmailMixin(object):

	def validate_invitation(self,email):
		if Invitation.objects.all_valid().filter(email__iexact=email, accepted=False):
			raise AlreadyInvited
		elif Invitation.objects.filter(email__iexact=email,accepted=True):
			raise AlreadyAccepted
		elif User.objects.filter(email__iexact=email):
			raise UserRegisteredEmail
		else:
			return True