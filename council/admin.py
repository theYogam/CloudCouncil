from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Register your models here.
from conf import settings
from ikwen_kakocase.kakocase.models import ProductCategory
from ikwen_kakocase.kakocase.admin import ProductCategoryAdmin
from council.models import Profile, PaymentOrder, Tax


class ProfileAdmin(admin.ModelAdmin):
    fields = ('member', 'type', 'taxpayer')


class PaymentOrderAdmin(admin.ModelAdmin):
    fields = ('reference_id', 'amount', 'due_date', 'status')


class TaxAdmin(admin.ModelAdmin):
    fields = ('name', 'short_description', 'cost', 'duration_text', 'phone', 'email',
              'provider_share_rate', 'lang', 'keywords')


class PaymentAdmin(admin.ModelAdmin):
    fields = ('member', 'tax', 'status')