from django.db import models
from netaddr import IPAddress
from subnets.DNS.manager import *
import NetaddrCustomizations.models
def set_type(dns_type):
	if dns_type == '1BD':
		return '='
	elif dns_type == '2NA':
		return '+'
	elif dns_type == '3AN':
		return '^'
def assert_default_ttl(ttl):
	if type(ttl) == type(None):
		return 86400
	elif ttl == 0:
		return 86400
	else:
		return ttl

class DNS_name(models.Model):																#DNS MODEL
	name 		= models.CharField('DNS name', max_length = 255)							#DNS name regular expression
	ip_address	= NetaddrCustomizations.models.NetaddrIPAddressField('IP Address')			#DNS
	dns_type	= models.CharField('Type', max_length = 3 )									#DNS type
	description = models.TextField('Description', blank=True)								#DNS name description
	is_ipv6 	= models.BooleanField()														#DNS bool check IP version 6
	time_created 	= models.DateTimeField()												#DNS name creation time
	time_modified  	= models.DateTimeField()												#DNS name modification time
	ttl			= models.IntegerField('Time to Live', default = 0)							#DNS time to live field
	objects 	= NameManager()
	def ExportRepresentation(self):
		return u'%s\t%s\t%s\t%s\t#%s\n' % (set_type(self.dns_type), self.ip_address, self.name, assert_default_ttl(self.ttl), self.description )
	def LogRepresentation(self):
		return u'{\'name\':\'%s\', \'ip_address\':IPAddress(\'%s\'), \'dns_type\':\'%s\', \'description\':\'%s\', \'ttl\':%s}' % (self.name, self.ip_address, self.dns_type, self.description, self.ttl )
	def __unicode__(self):
		return u'\'name\':\'%s\',\'ip_address\':\'%s\',\'is_ipv6\':\'%s\',\'dns_type\':\'%s\',\'description\':\'%s\', \'ttl\':%s'% (self.name, str(self.ip_address), self.is_ipv6, self.dns_type, self.description, self.ttl)
	class Meta:
        	ordering = ['ip_address','dns_type']
        	
