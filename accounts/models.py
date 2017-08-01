# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from smtplib import SMTPRecipientsRefused
from rest_framework.authtoken.models import Token

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .managers import BaseInvitationManager
from .adapters import BaseInvitationsAdapter

@python_2_unicode_compatible
class AbstractBaseInvitation(models.Model):
	accepted = models.BooleanField(verbose_name=_('accepted'),default=False)
	key = models.CharField(verbose_name=_('key'),max_length=64,unique=True)
	sent = models.DateTimeField(verbose_name=_('sent'),null=True)
	inviter = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True)

	objects = BaseInvitationManager()

	class Meta:
		abstract = True

	def __str__(self):
		raise NotImplementedError(
				"You must implement the __str__ method."
			)


@python_2_unicode_compatible
class Invitation(AbstractBaseInvitation):
	email = models.EmailField(unique=True,verbose_name=_('e-mail address'),max_length=255)
	created = models.DateTimeField(verbose_name=_('created'),default=timezone.now)

	@classmethod
	def create(cls, email, inviter=None, **kwargs):
		key = get_random_string(64).lower()
		instance = cls._default_manager.create(
			email=email,
			key=key,
			inviter=inviter,
			**kwargs
			)

		return instance

	def key_expired(self):
		expiration_date = (self.sent + datetime.timedelta(days=3))
		return expiration_date <= timezone.now()

	def send_invitation(self,request,**kwargs):
		current_site = (kwargs['site'] if 'site' in kwargs else Site.objects.get_current())
		invite_url = settings.SIGNUP_URL + str(self.key)

		ctx = {
			'invite_url':invite_url,
			'site_name':current_site.name,
			'email':self.email,
			'key':self.key,
			'inviter':self.inviter,
		}

		email_template = 'accounts/email/email_invite'

		try:
			BaseInvitationsAdapter().send_mail(email_template,self.email,ctx)
			self.sent = timezone.now()
			self.save()
		except(SMTPRecipientsRefused):
			self.delete()
			raise SMTPRecipientsRefused("SMTP Error")

	def __str__(self):
		return "Invite: {0}".format(self.email)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)