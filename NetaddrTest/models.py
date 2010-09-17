
from django.db import models

import NetaddrCustomizations.models

class TestAddress(models.Model):
	ip_address = NetaddrCustomizations.models.NetaddrIPAddressField('ip_address')

	def __unicode__(self):
		return str(self.ip_address)

