from django.db import models
from django.contrib.auth.models import Group
from netaddr import IPAddress, IPNetwork

__all__ = ['NetGroup', 'DNS_ipval', 'DNS_expr']

# ---- #
class DNS_expr(models.Model):
	expression 	= models.CharField('Expression', max_length = 100, unique=True)	#DNS name regular expression
	def __unicode__(self):
		return self.expression

class DNS_ipval(models.Model):
	ip_value	= models.CharField('IP Subnet', max_length = 100, unique=True)		#DNS ip address expression
	def __unicode__(self):
		return self.ip_value
	
class NetGroup(models.Model):
	name		= models.CharField('Network Resource', max_length=40, unique=True) 
	managed_by	= models.ManyToManyField( Group, blank=True) 
	address_blocks	= models.ManyToManyField( DNS_ipval, blank=True) 
	dns_patterns	= models.ManyToManyField( DNS_expr, blank=True)
	#description 	= models.TextField('Description',blank=True, null=True)	
	def __unicode__(self):
		return self.name
		


