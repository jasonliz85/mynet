
import netaddr

from django.core import exceptions
from django.db   import models

import forms

V4LIMIT = 1L << 32

def db4ip(ipaddress):
    return '%1d%032x' % (ipaddress.version, ipaddress.value)

def db4value(value):
    if value < V4LIMIT:
        version = 4
    else:
        version = 6
    return '%1d%032x' % (version, value)

class NetaddrIPAddressField(models.Field):
    """
    A Django Field class to represent IP addresses using the 'netaddr' package
    """
    description = "An IP address represented using the 'netaddr' package"

    __metaclass__ = models.SubfieldBase

    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 33
        super(NetaddrIPAddressField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def get_prep_value(self, value):
        return db4ip(value)

    def get_db_prep_value(self, value):
        return db4ip(value)

    def value_to_string(self, value):
        return db4ip(value)

    def to_python(self, value):
        if value is None:
            return value
        if not isinstance(value, basestring):
            return value
        try:
            version = int(value[0])
            value = int(value[1:], 16)
            return netaddr.IPAddress(value, version=version)
        except:
            raise exceptions.ValidationError(u'Enter a valid IP Address')

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.NetaddrIPAddressField}
        defaults.update(kwargs)
        return super(NetaddrIPAddressField, self).formfield(**defaults)

class NetaddrIPAddressAsIntegerField(models.Field):
    """
    A Django Field class to represent IP addresses using the 'netaddr' package
    but using the integer values used internally within that package
    """
    description = "An IP address represented using the 'netaddr' package"

    __metaclass__ = models.SubfieldBase

    empty_strings_allowed = False

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 33
        super(NetaddrIPAddressAsIntegerField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def get_prep_value(self, value):
        return db4value(value)

    def get_db_prep_value(self, value):
        return db4value(value)

    def value_to_string(self, value):
        return db4value(value)

    def to_python(self, value):
        if value is None:
            return value
        if not isinstance(value, basestring):
            return value
        try:
            version = int(value[0])
            value = int(value[1:], 16)
            return netaddr.IPAddress(value, version=version).value
        except:
            raise exceptions.ValidationError(u'Enter a valid IP Address')

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.NetaddrIPAddressAsIntegerField}
        defaults.update(kwargs)
        return super(NetaddrIPAddressAsIntegerField, self).formfield(**defaults)

