from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import admin

from pinsview.views import save_optical_fiber_position, save_device_position, \
    delete_old_way, save_live_optical_fiber_coords, BaseView, filter_network_data, \
    find_lines, is_registered_member, search, get_techie_installation, get_selected_fiber, get_selected_device, \
    get_recent_equipments, Network, change_device_position, grab_fibers, grab_devices, save_device, grab_device_info, \
    update_fibers_distance, check_new_fiber, check_new_device, check_data_integrity, check_line_update, Statistic, \
    get_specific_fiber_data, get_specific_device_data, get_updated_fibers, load_equipments_by_city, grab_fiber_info, \
    get_asset_event_log, save_event_log, grab_event_log_detail, grab_offline_devices,update_device_cities,\
    save_asset_config, grab_asset_config, save_prospect, update_prospect_status

from admin_panel import *

SIGN_IN = 'login'
_extra_context = BaseView().get_context_data()

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', login_required()(Network.as_view()), name='network'),

    url(r'^changeCategory/$', ChangeDeviceCategory.as_view(), name='change_devicecategory'),
    url(r'^changeCategory/(?P<object_id>[-\w]+)$', ChangeDeviceCategory.as_view(), name='change_devicecategory'),
    url(r'^categoryList$', DeviceCategoryList.as_view(), name='devicecategory_list'),

    url(r'^changePin/$', ChangeDevice.as_view(), name='change_device'),
    url(r'^changePin/(?P<object_id>[-\w]+)$', ChangeDevice.as_view(), name='change_device'),
    url(r'^pinList$', DeviceList.as_view(), name='device_list'),

    url(r'^changeCity/$', ChangeCity.as_view(), name='change_city'),
    url(r'^changeCity/(?P<object_id>[-\w]+)$', ChangeCity.as_view(), name='change_city'),
    url(r'^cityList$', CityList.as_view(), name='city_list'),

    url(r'^findFiberlines', find_lines, name='find_lines'),
    url(r'^statistics$', user_passes_test(is_registered_member)(Statistic.as_view()), name='statistic'),
    url(r'^save_device$', save_device, name='save_device'),
    url(r'^save_device_position$', save_device_position, name='save_device_position'),
    url(r'^save_live_optical_fiber_coords$', save_live_optical_fiber_coords, name='save_live_optical_fiber_coords'),
    url(r'^filter_network_data$', filter_network_data, name='filter_network_data'),
    url(r'^delete_old_way$', delete_old_way, name='delete_old_way'),
    url(r'^save_fiber_way$', save_optical_fiber_position, name='save_fiber_way'),
    url(r'^full_search$', search, name='search'),
    url(r'^get_selected_device$', get_selected_device, name='get_selected_device'),
    url(r'^get_selected_fiber$', get_selected_fiber, name='get_selected_fiber'),
    url(r'^change_device_position$', change_device_position, name='change_device_position'),
    url(r'^get_techie_installation$', get_techie_installation, name='get_techie_installation'),
    url(r'^get_recent_equipments$', get_recent_equipments, name='get_recent_equipments'),
    url(r'^grab_fibers$', grab_fibers, name='grab_fibers'),
    url(r'^grab_devices$', grab_devices, name='grab_devices'),
    url(r'^grab_device_info$', grab_device_info, name='grab_device_info'),
    url(r'^grab_fiber_info$', grab_fiber_info, name='grab_fiber_info'),
    url(r'^update_fibers_distance$', update_fibers_distance, name='update_fibers_distance'),
    url(r'^check_new_fiber$', check_new_fiber, name='check_new_fiber'),
    url(r'^check_new_device$', check_new_device, name='check_new_device'),
    url(r'^check_device_data_integrity$', check_data_integrity, name='check_data_integrity'),
    url(r'^check_line_update$', check_line_update, name='check_line_update'),
    url(r'^get_specific_fiber_data$', get_specific_fiber_data, name='get_specific_fiber_data'),
    url(r'^get_specific_device_data$', get_specific_device_data, name='get_specific_device_data'),
    url(r'^get_updated_fibers$', get_updated_fibers, name='get_updated_fibers'),
    url(r'^load_equipments_by_city$', load_equipments_by_city, name='load_equipments_by_city'),

    url(r'^get_asset_event_log$', get_asset_event_log, name='get_asset_event_log'),
    url(r'^save_asset_config$', save_asset_config, name='save_asset_config'),
    url(r'^save_event_log$', save_event_log, name='save_event_log'),
    url(r'^grab_event_log_detail$', grab_event_log_detail, name='grab_event_log_detail'),
    url(r'^grab_asset_config$', grab_asset_config, name='grab_asset_config'),
    url(r'^grab_offline_devices$', grab_offline_devices, name='grab_offline_devices'),

    url(r'^update_device_cities$', update_device_cities, name='update_device_cities'),
    url(r'^save_prospect$', save_prospect, name='save_prospect'),
    url(r'^update_prospect$', update_prospect_status, name='update_prospect_status'),
)