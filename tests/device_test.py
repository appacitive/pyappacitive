__author__ = 'sathley'

from pyappacitive import AppacitiveDevice, AppacitiveError
import random
from pyappacitive import AppacitiveQuery, PropertyFilter
from nose.tools import *


def get_random_string(number_of_characters=10):
    arr = [str(i) for i in range(number_of_characters)]
    random.shuffle(arr)
    return ''.join(arr)


def get_random_device():
    device = AppacitiveDevice()
    device.devicetype = 'ios'
    device.devicetoken = get_random_string()
    device.location = '10.10,20.20'
    return device


def register_device_test():
    device = get_random_device()
    device.register()
    assert device.id > 0


def get_device_test():
    device = get_random_device()
    device.register()

    device1 = AppacitiveDevice.get(device.id)
    assert device1 is not None
    assert device1.id == device.id


def multi_get_device_test():
    device_ids = []
    for i in range(12):
        device = get_random_device()
        device.register()
        device_ids.append(device.id)
    devices = AppacitiveDevice.multi_get(device_ids)
    assert len(devices) == 12


def device_update_test():
    device = get_random_device()
    device.badge = 100
    device.register()

    device.badge = 200
    device.update()
    assert device.badge == 200


@raises(AppacitiveError)
def delete_device_test():
    device = get_random_device()
    device.register()
    device_id = device.id
    device.delete()

    device1 = AppacitiveDevice.get(device_id)


def find_device_test():
    device = get_random_device()
    device.register()
    query = AppacitiveQuery()
    query.filter = PropertyFilter('devicetype').is_equal_to('ios')
    response_collection = AppacitiveDevice.find(query)
    assert len(response_collection.devices) > 0