from django.db import models
from django.contrib.auth.models import Group
from netaddr import IPAddress

# ---- #
class DNS_expr(models.Model):
	expression 	= models.CharField('Expression', max_length = 100, unique=True)	#DNS name regular expression
	def __unicode__(self):
		return self.expression

class DNS_ipval(models.Model):
	ip_value	= models.CharField('IP Range', max_length = 100, unique=True)		#DNS ip address expression
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

def get_netgroups_managed_by_user(user_obj):
	"""
	Returns a list of NetGroup objects which the user can manage
	"""
	if not hasattr(user_obj, '_netgroup_cache') or True:
		netgroup_cache = []
		#print 'Starting loops'
		for g in user_obj.groups.all():
			#print 'Group', g
			for ng in g.netgroup_set.all():
				#print 'NetGroup', ng 
				if ng not in netgroup_cache: 
					netgroup_cache.append(ng)
		user_obj._netgroup_cache = netgroup_cache
	return	user_obj._netgroup_cache

def get_address_blocks_managed_by(user_obj):
	"""
	Returns a list of IP address block objects which the user can manage
	"""
	if not hasattr(user_obj, '_address_blocks') or True:
		address_blocks = [] #list containing all address blocks the user is allowed to change
		for netgroup in get_netgroups_managed_by_user(user_obj):
			for addressblock in netgroup.address_blocks.all():
				if addressblock not in address_blocks: 
					address_blocks.append(addressblock)
					#print address_blocks
		user_obj._address_blocks = address_blocks
		#print address_blocks
	return	user_obj._address_blocks

def get_dns_patterns_managed_by(user_obj):
	"""
	Returns a list of dns pattern objects which the user can manage
	"""
	if not hasattr(user_obj, '_dns_patterns') or True:
		dns_patterns = []
		for ng in get_netgroups_managed_by_user(user_obj):
			for dp in ng.dns_patterns.all():
				if dp not in dns_patterns: dns_patterns.append(dp)
		user_obj._dns_patterns = dns_patterns
	return	user_obj._dns_patterns

