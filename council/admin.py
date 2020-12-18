from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Register your models here.
from conf import settings
from ikwen_kakocase.kakocase.models import ProductCategory
from ikwen_kakocase.kakocase.admin import ProductCategoryAdmin
from council.models import Profile, PaymentOrder, Tax


class CategoryAdmin(admin.ModelAdmin):
    fields = ('name',)


class ProfileAdmin(admin.ModelAdmin):
    fields = ('member', 'business_type', 'taxpayer', 'location_lat', 'location_lng', 'formatted_address')


class PaymentOrderAdmin(admin.ModelAdmin):
    fields = ('reference_id', 'amount', 'due_date', 'status')


class TaxAdmin(admin.ModelAdmin):
    fields = ('name', 'short_description', 'cost', 'duration_text', 'phone', 'email',
              'provider_share_rate', 'lang', 'keywords')


class PaymentAdmin(admin.ModelAdmin):
    fields = ('member', 'tax', 'status')


class BannerAdmin(admin.ModelAdmin):
    fields = ('title_header',)


class ProjectAdmin(admin.ModelAdmin):
    fields = ('name', 'leader', 'cost', 'description',)
