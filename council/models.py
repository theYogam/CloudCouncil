from django.conf.global_settings import LANGUAGES
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models

# Create your models here.
from django.db.models import Model
from django.utils.translation import gettext_lazy as _

from ikwen.core.utils import slice_watch_objects, rank_watch_objects, add_database, set_counters, get_service_instance, \
    get_model_admin_instance, clear_counters, get_mail_content, XEmailMessage, add_event

from ikwen.core.models import Model, AbstractConfig, Service
from ikwen.core.fields import MultiImageField, FileField
# from ikwen.core.constants import PAYMENT_STATUS_CHOICES
from ikwen.accesscontrol.models import Member

from ikwen.billing.models import AbstractProduct, AbstractPayment
from ikwen_kakocase.kakocase.models import ProductCategory


PENDING = "Pending"
OVERDUE = "Overdue"
EXCEEDED = "Exceeded"
PAID = "Paid"
INVOICE_STATUS_CHOICES = (
    (PENDING, _("Pending")),
    (OVERDUE, _("Overdue")),
    (EXCEEDED, _("Exceeded")),
    (PAID, _("Paid")),
)


class Category(Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return self.name


class Tax(AbstractProduct):
    phone = models.CharField(max_length=60, blank=True, null=True,
                             help_text="Contact phone of support team")
    email = models.EmailField(blank=True, null=True,
                              help_text="Contact email of support team")
    provider_share_rate = models.FloatField(default=10)
    callback = models.CharField(max_length=255, blank=True,
                                help_text="Callback that is run after completion of payment of this product.")
    template_name = models.CharField(max_length=150, blank=True,
                                     help_text="Template of the detail page of the Product.")
    lang = models.CharField(max_length=30, choices=LANGUAGES, default='en')
    keywords = models.CharField(max_length=255, db_index=True, blank=True, null=True,
                            help_text="Search tags")


class PaymentOrder(Model):
    provider = models.ForeignKey(Member, blank=True, null=True)
    reference_id = models.CharField(_('Reference ID'), max_length=255, null=True, blank=True)
    amount = models.IntegerField(_('Amount'), default=0)
    due_date = models.DateField(_('Due date'))
    last_notice_date = models.DateTimeField(_('Last notice date'), null=True, blank=True)
    status = models.CharField(_('Status'), max_length=100, choices=INVOICE_STATUS_CHOICES)

    def __unicode__(self):
        return self.provider.full_name

    def get_obj_details(self):
        return 'Ref: %s : <strong style="color: #222">%s</strong>' % (self.reference_id, intcomma(self.amount))


class Payment(AbstractPayment):
    member = models.ForeignKey(Member)
    tax = models.ForeignKey(Tax)
    status = models.CharField(max_length=100, default=PENDING)

    def __unicode__(self):
        return _("%s of  XAF %s:  %s ") % (self.tax.name, intcomma(self.tax.cost), self.member.full_name)


class Profile(Model):

    member = models.ForeignKey(Member)
    business_type = models.ForeignKey(Category, null=True, blank=True)
    location_lat = models.FloatField(default=0.0, null=True, blank=True)
    location_lng = models.FloatField(default=0.0, null=True, blank=True)
    formatted_address = models.CharField(max_length=250, default='', null=True, blank=True)

    id_number = models.CharField(_('ID Card Number'), max_length=100)
    taxpayer = models.CharField(_('Taxpayer Number'),  max_length=100, blank=True, null=True)
    company_name = models.CharField(_('Company Name'), max_length=100, blank=True, null=True)

    def __unicode__(self):
        return "%s: %s" % (self.business_type, self.member.full_name)


class Banner(Model):
    UPLOAD_TO = 'Banner'
    title_header = models.CharField(_("Title's header"), blank=True, null=True)
    image = MultiImageField(_('Banner image'), allowed_extensions=['jpeg', 'png', 'jpg'],
                            upload_to=UPLOAD_TO, required_width=1920, null=True)


class Project(Model):
    name = models.CharField(_("Project's name"), max_length=150)
    leader = models.ForeignKey(Member)
    cost = models.IntegerField(_("Cost"), default=0)
    description = models.TextField(_("Project description"))
    attachment = FileField(_('Attachment'), allowed_extensions=['doc', 'docx', 'pdf', 'ppt', 'odt'],
                           upload_to='Projects')