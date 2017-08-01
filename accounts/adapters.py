
from django.template.loader import render_to_string
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, EmailMessage


try:
	from django.utils.encoding import force_text
except ImportError:
	from django.utils.encoding import force_unicode as force_text


class BaseInvitationsAdapter(object):

	def stash_verified_email(self,request,email):
		request.session['account_verified_email'] = email

	def unstash_verified_email(self,request):
		ret = request.session.get('account_verified_email')
		request.session['account_verified_email'] = None
		return ret

	def format_email_subject(self,subject):
		site = Site.objects.get_current()
		prefix = "[{name}] ".format(name=site.name)
		return prefix + force_text(subject)

	def render_mail(self,template_prefix,email,context):

		subject = render_to_string('{0}_subject.txt'.format(template_prefix),context)

		subject = " ".join(subject.splitlines()).strip()
		subject = self.format_email_subject(subject)

		bodies = {}
		for ext in ['html','txt']:
			try:
				template_name = '{0}_message.{1}'.format(template_prefix,ext)
				bodies[ext] = render_to_string(template_name,context).strip()

			except TemplateDoesNotExist:
				if ext == 'txt' and not bodies:
					raise

		if 'txt' in bodies:
			msg = EmailMultiAlternatives(subject,bodies['txt'],settings.DEFAULT_FROM_EMAIL,[email])

			if 'html' in bodies:
				msg.attach_alternative(bodies['html'],'text/html')
		else:
			msg = EmailMessage(subject,bodies['html'],settings.DEFAULT_FROM_EMAIL,[email])
			msg.content_subtype = 'html'

		return msg

	def send_mail(self,template_prefix,email,context):
		msg = self.render_mail(template_prefix,email,context)
		msg.send()

