"""
    This file consists of example models for e-comerce app based on Salest Core
    and Django.
    Every class should extend core class with basic interfaces.
"""

from django.db import models
from django import template
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template import Context

from model_fields import JSONField
import listeners

class A(object):
    pass

SIGNAL_TYPES = (
    ('PV', 'Page view'),
    ('PATC', 'Product added to cart'),
    ('PRFC', 'Product removed from cart')
)

#class EventManager(models.Manager):
#    """ This is custom model manager for Event class. Basically it should define
#        custom database for this class. """
#
#    def __init__(self, db_name):
#        """ custom init """
#        super(EventManager, self).__init__()
#        self._db = db_name
#
#
class Event(models.Model):
    """ This model should store some information about signals."""
    signal_type = models.CharField(choices=SIGNAL_TYPES, max_length=5)
    signal_info = JSONField(max_length=200)

#    objects = EventManager("event_storage")


class EmailTemplate(models.Model):
    """ Email Templates """
    subject = models.CharField(max_length=255, blank=True, null=True)
    to_email = models.CharField(max_length=255, blank=True, null=True)
    from_email = models.CharField(max_length=255, blank=True, null=True)
    html_template = models.TextField(blank=True, null=True)
    plain_text = models.TextField(blank=True, null=True)
    is_html = models.BooleanField()
    is_text = models.BooleanField()
    template_key = models.CharField(max_length=255, unique=True)

#    @staticmethod
    def get_rendered_template(self, tpl, context):
        """ """
        return self.get_template(tpl).render(context)

#    @staticmethod
    def get_template(self, tpl):
        """ """
        return template.Template(tpl)

    def get_subject(self, subject, context):
        """ get subject """
        return subject or self.get_rendered_template(self.subject, context)

    def get_body(self, body, context):
        """ get body """
        return body or self.get_rendered_template(self._get_body(), context)

    def get_sender(self):
        """ get sender """
        return self.from_email or settings.DEFAULT_FROM_EMAIL

    def get_recipient(self, emails, context):
        """ get_recipient """
        return emails or [self.get_rendered_template(self.to_email, context)]

    @staticmethod
    def send(template_key, context, subject=None, body=None, sender=None,
             emails=None):
        """ send email """
        mail_template = EmailTemplate.objects.get(template_key=template_key)
        context = Context(context)

        subject = mail_template.get_subject(subject, context)
        body = mail_template.get_body(body, context)
        sender = sender or mail_template.get_sender()
        emails = mail_template.get_recipient(emails, context)

        if mail_template.is_text:
            return send_mail(subject, body, sender, emails, fail_silently=not
                             settings.EMAIL_DEBUG)

        msg = EmailMultiAlternatives(subject, '', sender, emails)
        msg.attach_alternative(body, "text/html")
        return msg.send(fail_silently=not settings.EMAIL_DEBUG)


    def _get_body(self):
        """ """
        if self.is_text:
            return self.plain_text

        return self.html_template

    def __unicode__(self):
        """ """
        return "<" + self.template_key + "> " + self.subject
