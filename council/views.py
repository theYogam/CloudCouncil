import logging
import random
import string
from datetime import timedelta, datetime
from threading import Thread

# Create your views here.

import requests
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView

from ikwen.accesscontrol.models import Member
from ikwen.conf.settings import WALLETS_DB_ALIAS
from ikwen.core.constants import CONFIRMED
from ikwen.core.templatetags.url_utils import strip_base_alias
from ikwen.core.utils import increment_history_field
from ikwen.billing.models import MoMoTransaction, MTN_MOMO
from ikwen.billing.utils import get_next_invoice_number

from ikwen.core.views import HybridListView, DashboardBase, ChangeObjectBase
from ikwen.core.utils import set_counters, get_service_instance, \
    get_mail_content
from ikwen.billing.invoicing.views import Payment

from council.models import PaymentOrder, Profile, Tax, Payment, Banner, Project, Category
from council.admin import PaymentOrderAdmin, ProfileAdmin, TaxAdmin, PaymentAdmin, BannerAdmin, ProjectAdmin, CategoryAdmin
from pinsview.models import Pin, PinCategory, City, Zone

logger = logging.getLogger('ikwen')


class Dashboard(DashboardBase):
    # template_name = 'council/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        return context


class Home(HybridListView):
    model = Tax
    model_admin = TaxAdmin
    template_name = 'council/show_tax_list.html'
    html_results_template_name = 'council/snippets/tax_list_results.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        config = get_service_instance().config
        created_profile = False
        if self.request.user.is_authenticated():
            if Profile.objects.filter(member=self.request.user):
                created_profile = True
        context['created_profile'] = created_profile
        context['banner'] = Banner.objects.first()
        context['currency_symbol'] = config.currency_symbol
        return context


class ChangeTax(ChangeObjectBase):
    model = Tax
    model_admin = TaxAdmin


class TaxList(HybridListView):
    model = Tax
    model_admin = TaxAdmin


class ChangeBanner(ChangeObjectBase):
    model = Banner
    model_admin = BannerAdmin


class BannerList(HybridListView):
    model = Banner
    model_admin = BannerAdmin


class PaymentOrderList(HybridListView):
    model = PaymentOrder
    model_admin = PaymentOrderAdmin


class Receipt(TemplateView):
    template_name = 'council/receipt.html'

    def get_context_data(self, **kwargs):
        context = super(Receipt, self).get_context_data(**kwargs)
        config = get_service_instance().config
        receipt_id = self.kwargs.get('receipt_id')
        try:
            payment = Payment.objects.select_related('tax', 'member').get(pk=receipt_id)
        except Payment.DoesNotExist:
            raise Http404("Payment not found")
        context['currency_symbol'] = config.currency_symbol
        context['payment'] = payment
        context['member'] = payment.member
        context['amount'] = payment.tax.cost
        context['payment_number'] = get_next_invoice_number()
        return context


class PaymentList(HybridListView):
    model = Payment
    model_admin = PaymentAdmin


class ChangePaymentOrder(ChangeObjectBase):
    model = PaymentOrder
    model_admin = PaymentOrderAdmin

    def after_save(self, request, obj, *args, **kwargs):
        member_id = request.POST['member_id']
        member = Member.objects.get(pk=member_id)
        obj.provider = member
        obj.save()


class EditProfile(ChangeObjectBase):
    template_name = 'council/edit_profile.html'
    model = Profile
    model_admin = ProfileAdmin

    def get_context_data(self, **kwargs):
        context = super(EditProfile, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        try:
            context['profile'] = Profile.objects.get(member=self.request.user)
        except:
            pass
        return context

    def get_object(self, **kwargs):
        if self.request.user.is_authenticated():
            try:
                profile = Profile.objects.get(member=self.request.user)
            except:
                profile = Profile.objects.create(member=self.request.user)
            return profile

    def after_save(self, request, obj):
        try:
            category = PinCategory.objects.get(name=obj.business_type.name)
        except:
            category = PinCategory.objects.create(name=obj.business_type.name)
        try:
            city = City.objects.get(name=obj.formatted_address.split(',')[1])
        except:
            city = City.objects.create(name=obj.formatted_address.split(',')[1])
        try:
            zone = Zone.objects.get(name=obj.formatted_address.split(',')[0], city=city)
        except:
            zone = Zone.objects.create(name=obj.formatted_address.split(',')[0], city=city)
        Pin.objects.create(category=category, name=obj.member.full_name,
                              city=city, latitude=obj.location_lat,
                              longitude=obj.location_lng, created_on=obj.created_on, updated_on=obj.updated_on)
        return HttpResponseRedirect(reverse('home') + "?profile_created=yes")


class ChangeCategory(ChangeObjectBase):
    model = Category
    model_admin = CategoryAdmin


class CategoryList(HybridListView):
    model = Category


class ProjectList(HybridListView):
    model = Project
    model_admin = ProjectAdmin


class ChangeProject(ChangeObjectBase):
    model = Project
    model_admin = ProjectAdmin


class ChangeProfile(ChangeObjectBase):
    model = Profile
    model_admin = ProfileAdmin
    template_name = 'council/change_profile.html'


class ProfileList(HybridListView):
    model = Profile


def set_momo_payment(request, *args, **kwargs):
    service = get_service_instance()
    config = service.config
    product_id = request.POST['product_id']
    product = Tax.objects.get(pk=product_id)
    payment = Payment.objects.create(member=request.user, tax=product, method=Payment.MOBILE_MONEY,
                                     amount=product.cost)
    model_name = 'council.Payment'
    mean = request.GET.get('mean', MTN_MOMO)
    signature = ''.join([random.SystemRandom().choice(string.ascii_letters + string.digits) for i in range(16)])
    MoMoTransaction.objects.using(WALLETS_DB_ALIAS).filter(object_id=product.id).delete()
    tx = MoMoTransaction.objects.using(WALLETS_DB_ALIAS)\
        .create(service_id=service.id, type=MoMoTransaction.CASH_OUT, amount=product.cost, phone='N/A', model=model_name,
                object_id=payment.id, task_id=signature, wallet=mean, username=request.user.username, is_running=True)
    notification_url = reverse('council:confirm_payment', args=(tx.id, signature))
    cancel_url = reverse('home')

    return_url = reverse('council:receipt', args=(payment.id, ))
    gateway_url = getattr(settings, 'IKWEN_PAYMENT_GATEWAY_URL', 'http://payment.ikwen.com/v1')
    endpoint = gateway_url + '/request_payment'
    user_id = request.user.username if request.user.is_authenticated() else '<Anonymous>'
    params = {
        'username': getattr(settings, 'IKWEN_PAYMENT_GATEWAY_USERNAME', service.project_name_slug),
        'amount': product.cost,
        'merchant_name': config.company_name,
        'notification_url': service.url + strip_base_alias(notification_url),
        'return_url': service.url + strip_base_alias(return_url),
        'cancel_url': service.url + strip_base_alias(cancel_url),
        'user_id': user_id
    }
    try:
        r = requests.get(endpoint, params)
        resp = r.json()
        token = resp.get('token')
        if token:
            next_url = gateway_url + '/checkoutnow/' + resp['token'] + '?mean=' + mean
            messages.success(request, 'You successfully paid your tax name' + product.name)
        else:
            logger.error("%s - Init payment flow failed with URL %s and message %s" % (service.project_name, r.url, resp['errors']))
            messages.error(request, resp['errors'])
            next_url = cancel_url
    except:
        logger.error("%s - Init payment flow failed with URL." % service.project_name, exc_info=True)
        next_url = cancel_url
    return HttpResponseRedirect(next_url)


def confirm_payment(request, *args, **kwargs):
    status = request.GET['status']
    message = request.GET['message']
    operator_tx_id = request.GET['operator_tx_id']
    phone = request.GET['phone']
    tx_id = kwargs['tx_id']
    try:
        tx = MoMoTransaction.objects.using(WALLETS_DB_ALIAS).get(pk=tx_id)
        if not getattr(settings, 'DEBUG', False):
            tx_timeout = getattr(settings, 'IKWEN_PAYMENT_GATEWAY_TIMEOUT', 15) * 60
            expiry = tx.created_on + timedelta(seconds=tx_timeout)
            if datetime.now() > expiry:
                return HttpResponse("Transaction %s timed out." % tx_id)
    except:
        raise Http404("Transaction %s not found" % tx_id)

    callback_signature = kwargs.get('signature')
    no_check_signature = request.GET.get('ncs')
    if getattr(settings, 'DEBUG', False):
        if not no_check_signature:
            if callback_signature != tx.task_id:
                return HttpResponse('Invalid transaction signature')
    else:
        if callback_signature != tx.task_id:
            return HttpResponse('Invalid transaction signature')

    if status != MoMoTransaction.SUCCESS:
        return HttpResponse("Notification for transaction %s received with status %s" % (tx_id, status))

    tx.status = status
    tx.message = message
    tx.processor_tx_id = operator_tx_id
    tx.phone = phone
    tx.is_running = False
    tx.save()
    payment = Payment.objects.select_related('member', 'tax').get(pk=tx.object_id)
    payment.status = CONFIRMED
    payment.processor_tx_id = operator_tx_id
    payment.save()

    tax = payment.tax
    weblet = get_service_instance(check_cache=False)
    weblet.raise_balance(tx.amount, provider=tx.wallet)
    payer = payment.member
    profile_payer = Profile.objects.get(member=payer)
    set_counters(weblet)
    increment_history_field(weblet, 'turnover_history', tx.amount)
    increment_history_field(weblet, 'earnings_history', tx.amount)
    increment_history_field(weblet, 'transaction_count_history')

    email = tax.email
    config = weblet.config
    if not email:
        email = config.contact_email
    if not email:
        email = weblet.member.email
    if email or payer.email:
        subject = _("Successful payment of %s" % tax.name)
        try:
            html_content = get_mail_content(subject, template_name='council/mails/payment_notice.html',
                                            extra_context={'currency_symbol': config.currency_symbol,
                                                           'product': tax,
                                                           'payer': payer,
                                                           'profile_payer': profile_payer,
                                                           'tx_date': tx.updated_on.strftime('%Y-%m-%d'),
                                                           'tx_time': tx.updated_on.strftime('%H:%M:%S')})
            sender = '%s <no-reply@%s>' % (weblet.project_name, weblet.domain)
            msg = EmailMessage(subject, html_content, sender, [payer.email])
            msg.bcc = [email]
            msg.content_subtype = "html"
            if getattr(settings, 'UNIT_TESTING', False):
                msg.send()
            else:
                Thread(target=lambda m: m.send(), args=(msg,)).start()
        except:
            logger.error("%s - Failed to send notice mail to %s." % (weblet, email), exc_info=True)
    return HttpResponse("Notification successfully received")


class Maps(TemplateView):
    template_name = 'council/maps.html'

    def get_context_data(self, **kwargs):
        context = super(Maps, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context

    def get(self, request, *args, **kwargs):
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        formatted_address = request.GET.get('formatted_address')
        if lat and lng and formatted_address:
            return HttpResponseRedirect(reverse('council:edit_profile') + "?lat=" + lat + "&lng=" + lng +
                                        "&formatted_address=" + formatted_address)
        return super(Maps, self).get(request, *args, **kwargs)


def notify_outdated_payment_orders(request, *args, **kwargs):
    now = datetime.now()
    weblet = get_service_instance()
    config = weblet.config
    for obj in PaymentOrder.objects.filter(due_date__lt=now.date()):
        if obj.last_notice_date:
            diff = now - obj.last_notice_date
            if diff.total_seconds() < 86400:
                continue
        # Send notification here by email
        subject = _("Outdated Payment Order")
        html_content = get_mail_content(subject, template_name='council/mails/outdate_payment_orders_notice.html',
                                        extra_context={'currency_symbol': config.currency_symbol,
                                                       'payment_order': obj,
                                                       'ref_id': obj.reference_id,
                                                       'provider': obj.provider,
                                                       'project_name': weblet.project_name,
                                                       'due_date': obj.due_date.strftime('%Y-%m-%d'),
                                                       'issue_date': obj.created_on.strftime('%Y-%m-%d')})
        sender = '%s <no-reply@%s>' % (weblet.project_name, weblet.domain)
        msg = EmailMessage(subject, html_content, sender, [config.contact_email])
        msg.cc = ["silatchomsiaka@gmail.com"]
        msg.content_subtype = "html"
        if getattr(settings, 'UNIT_TESTING', False):
            msg.send()
        else:
            Thread(target=lambda m: m.send(), args=(msg,)).start()
    messages.success(request, _('Email sent'),)

    return HttpResponseRedirect(reverse('home'))
