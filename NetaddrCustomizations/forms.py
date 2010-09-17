
import netaddr

from django import forms

class NetaddrIPAddressField(forms.Field):
    """
    A Django Form Field class to represent IP addresses using the 'netaddr' package
    """

    default_error_messages = {
        'invalid': u'Enter a valid IP address',
    }

    def clean(self, value):
        super(NetaddrIPAddressField, self).clean(value)
        if isinstance(value, netaddr.IPAddress):
            return value
        try:
            value = netaddr.IPAddress(value)
        except:
            raise forms.ValidationError(self.error_messages['invalid'])
        return value

class NetaddrIPAddressAsIntegerField(forms.Field):
    """
    A Django Form Field class to represent IP addresses using the 'netaddr' package
    """

    default_error_messages = {
        'invalid': u'Enter a valid IP address',
    }

    def clean(self, value):
        super(NetaddrIPAddressField, self).clean(value)
        if isinstance(value, netaddr.IPAddress):
            return value
        try:
            value = netaddr.IPAddress(value)
        except:
            raise forms.ValidationError(self.error_messages['invalid'])
        return value.value

