# Forked and reviewed by Silatchom SIAKA on June 10, Wed 2020
import os
import sys
import logging
import socket
import subprocess
import paramiko
from datetime import datetime
from ftplib import FTP

sys.path.append("/home/libran/virtualenv/lib/python2.7/site-packages")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'conf.settings')


from datetime import timedelta, datetime
from threading import Thread
# Create your views here.


from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import activate, ugettext as _
from ikwen.core.utils import slice_watch_objects, rank_watch_objects, add_database, set_counters, get_service_instance, \
    get_model_admin_instance, clear_counters, get_mail_content
from ikwen.core.log import CRONS_LOGGING

from council.models import PaymentOrder


logging.config.dictConfig(CRONS_LOGGING)
logger = logging.getLogger('ikwen.crons')


def notify_staff():
    now = datetime.now()
    weblet = get_service_instance()
    config = weblet.config
    for obj in PaymentOrder.objects.filter(due_date__lt=now.date()):
        print "Processing notification of payment %f of ref %s\n" % (obj.amount, obj.reference_id)
        if obj.last_notice_date:
            diff = now - obj.last_notice_date
            if diff.total_seconds() < 86400:
                print "Skipping Payment of ref: %s\n" % obj.reference_id
                continue
        # Send notification here by email
        subject = _("Outdated Payment Order")
        html_content = get_mail_content(subject, template_name='council/mails/outdate_payment_orders_notice.html',
                                        extra_context={'currency_symbol': config.currency_symbol,
                                                       'payment_order': obj,
                                                       'ref_id': obj.reference_id,
                                                       'provider': obj.provider,
                                                       'due_date': obj.due_date.strftime('%Y-%m-%d'),
                                                       'issue_date': obj.created_on.strftime('%Y-%m-%d')})
        sender = '%s <no-reply@%s>' % (weblet.project_name, weblet.domain)
        msg = EmailMessage(subject, html_content, sender, [config.contact_email])
        msg.content_subtype = "html"
        if getattr(settings, 'UNIT_TESTING', False):
            msg.send()
        else:
            Thread(target=lambda m: m.send(), args=(msg,)).start()
            print "Sending email of outdated payment order to %s\n" % config.contact_email


if __name__ == '__main__':
    try:
        notify_staff()
    except:
        logger.error(u"Failed to send email of failed backups to staff", exc_info=True)
