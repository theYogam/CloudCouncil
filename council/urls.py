
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required, permission_required

from council.views import Home, PaymentOrderList, Dashboard, ChangeTax, TaxList, Receipt, ChangePaymentOrder, \
    EditProfile, ProfileList, set_momo_payment, confirm_payment, PaymentList, Maps, \
    notify_outdated_payment_orders, ChangeProfile, ChangeBanner, BannerList, ProjectList, ChangeProject, CategoryList, ChangeCategory

urlpatterns = patterns(
    '',

    url(r'^kmth/dashboard/$', permission_required('council.ik_manage_dashboard')(Dashboard.as_view()),
                                                                                name='dashboard'),


    url(r'^kmth/payments/$', permission_required('council.ik_manage_payment')(PaymentList.as_view()), name='payment_list'),


    url(r'^kmth/categoryList/$', permission_required('council.ik_manage_category')(CategoryList.as_view()), name='category_list'),
    url(r'^kmth/changeCategory/$', permission_required('council.ik_manage_category')(ChangeCategory.as_view()), name='change_category'),
    url(r'^kmth/changeCategory/(?P<object_id>[-\w]+)$', permission_required('council.ik_manage_category')(ChangeCategory.as_view()),
        name='change_category'),

    url(r'^kmth/taxList/$', permission_required('council.ik_manage_tax')(TaxList.as_view()), name='tax_list'),
    url(r'^kmth/changeTax/$', permission_required('council.ik_manage_tax')(ChangeTax.as_view()), name='change_tax'),
    url(r'^kmth/changeTax/(?P<object_id>[-\w]+)$', permission_required('council.ik_manage_tax')(ChangeTax.as_view()),
        name='change_tax'),


    url(r'^kmth/changeProfile/$', permission_required('council.ik_view_profile')(ChangeProfile.as_view()), name='change_profile'),
    url(r'^kmth/changeProfile/(?P<object_id>[-\w]+)/$',
        permission_required('council.ik_view_profile')(ChangeProfile.as_view()), name='change_profile'),
    url(r'^kmth/profileList/$', permission_required('council.ik_view_profile')(ProfileList.as_view()), name='profile_list'),


    url(r'^kmth/changeProject/$', permission_required('council.ik_view_project')(ChangeProject.as_view()),
        name='change_project'),
    url(r'^kmth/changeProject/(?P<object_id>[-\w]+)/$',
        permission_required('council.ik_view_profile')(ChangeProject.as_view()), name='change_project'),
    url(r'^kmth/projectList/$', permission_required('council.ik_view_project')(ProjectList.as_view()),
        name='project_list'),

    url(r'^kmth/paymentOrderList$',
        permission_required('council.ik_manage_payment_order')(PaymentOrderList.as_view()),
        name='paymentorder_list'),
    url(r'^kmth/changePaymentOrder/$',
        permission_required('council.ik_manage_payment_order')(ChangePaymentOrder.as_view()),
        name='change_paymentorder'),
    url(r'^kmth/changePaymentOrder/(?P<object_id>[-\w]+)$',
        permission_required('council.ik_manage_payment_order')(ChangePaymentOrder.as_view()), name='change_paymentorder'),


    url(r'^kmth/BannerList/$', permission_required('council.ik_manage_tax')(BannerList.as_view()), name='banner_list'),
    url(r'^kmth/changeBanner/$', permission_required('council.ik_manage_tax')(ChangeBanner.as_view()), name='change_banner'),
    url(r'^kmth/changeBanner/(?P<object_id>[-\w]+)$', permission_required('council.ik_manage_tax')(ChangeBanner.as_view()),
        name='change_banner'),


    # url(r'^home/$', Home.as_view(), name='home'),
    url(r'^profie/edit$', login_required(EditProfile.as_view()), name='edit_profile'),
    url(r'^maps$', login_required(Maps.as_view()), name='maps'),
    url(r'^receipt/(?P<receipt_id>[-\w]+)/$', login_required(Receipt.as_view()), name='receipt'),

    url(r'^set_momo_payment$', set_momo_payment),
    url(r'^confirm_payment/(?P<tx_id>[-\w]+)/(?P<signature>[-\w]+)$', confirm_payment, name='confirm_payment'),

    url(r'^notif$', notify_outdated_payment_orders, name='notify_outdated_payment_orders'),
)
