from ikwen.core.views import HybridListView, ChangeObjectBase

from pinsview.admin import DeviceAdmin, DeviceCategoryAdmin, CityAdmin

from pinsview.models import Device, DeviceCategory, City


class DeviceList(HybridListView):
    model = Device


class ChangeDevice(ChangeObjectBase):
    model = Device
    model_admin = DeviceAdmin


class DeviceCategoryList(HybridListView):
    model = DeviceCategory


class ChangeDeviceCategory(ChangeObjectBase):
    model = DeviceCategory
    model_admin = DeviceCategoryAdmin


class CityList(HybridListView):
    model = City


class ChangeCity(ChangeObjectBase):
    model = City
    model_admin = CityAdmin