from django.db import models
from django.contrib.auth.models import Group
from netaddr import IPAddress, IPNetwork
import NetaddrCustomizations.models

__all__ = ['NetGroup', 'ip_subnet', 'dns_expression']

# ---- #
class dns_expression(models.Model):
	expression 	= models.CharField('Expression', max_length = 100, unique=True)		#Network Resource Regular Expression
	description = models.TextField('Description', blank=True )			#Description of IP Subnet
	def __unicode__(self):
		return self.expression
	class Meta:
		ordering = ['expression']

class ip_subnet(models.Model):
	ip_network 	= NetaddrCustomizations.models.NetaddrIPNetworkField('IP Network', unique=True)
	@property
    	def ip_value(self): return str(self.ip_network)
	vlan		= models.IntegerField('Virtual LAN', blank=True )		#Virtual LAN number
	description = models.TextField('Description', blank=True )			#Description of IP Subnet
	def __unicode__(self):
		return str(self.ip_network)
	class Meta:
		ordering = ['ip_network']
	
class NetGroup(models.Model):
	name		= models.CharField('Network Resource', max_length=40, unique=True) 
	managed_by	= models.ManyToManyField( Group, blank=True) 
	address_blocks	= models.ManyToManyField( ip_subnet, blank=True) 
	dns_patterns	= models.ManyToManyField( dns_expression, blank=True)
	#description 	= models.TextField('Description',blank=True, null=True)	
	def __unicode__(self):
		return self.name
	class Meta:
		ordering = ['name']

