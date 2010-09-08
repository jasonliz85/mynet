from django.db import models

from django.contrib.auth.models import Group

from netaddr import IPAddress

class DNS_names(models.Model):							#DNS NAMING MODEL
	name 		= models.CharField('DNS name', max_length = 255)	#DNS name regular expression
	ip_address	= models.IntegerField('IP address')			#DNs ip address pair
	dns_type	= models.CharField('Type', max_length = 3 )		#DNS type
	description 	= models.TextField('Description', blank=True, null=True)#DNS name description
	is_ipv6 	= models.BooleanField()					#DNS bool check IP version 6
	time_created 	= models.DateTimeField()				#DNS name creation time
	time_modified  	= models.DateTimeField()				#DNS name modification time
	def LogRepresentation(self):
		return u'{\'name\':\'%s\', \'ip_address\':%s, \'dns_type\':\'%s\', \'description\':\'%s\'}' % (self.name, self.ip_address, self.dns_type, self.description )
	def __unicode__(self):
		return u'\'name\':\'%s\',\'ip_address\':\'%s\',\'is_ipv6\':\'%s\',\'dns_type\':\'%s\',\'description\':\'%s\''% (self.name, str(IPAddress(self.ip_address)), self.is_ipv6, self.dns_type, self.description)
	class Meta:
        	ordering = ['ip_address','dns_type']

class DHCP_machine(models.Model): 						#DHCP MACHINE REGISTRATION MODEL
	mac_address	= models.CharField('MAC address', max_length = 40)	#DHCP MAC address
	ip_address	= models.IntegerField('IP address')			#DHCP IP address 
	host_name	= models.CharField('Host name', max_length = 63)	#DHCP Host name
	is_ipv6 	= models.BooleanField()					#DHCP bool check IP version 6
	description 	= models.TextField('Description',blank=True, null=True)	#DHCP machine description of machine (optional)
	time_created 	= models.DateTimeField()				#DHCP machine registration creation time	
	time_modified	= models.DateTimeField()				#DHCP machine registration modification time	
	#is_ipv6
	#MAC_pair
	#IP_pair
	#PC_pair
	def LogRepresentation(self):
		return u'{\'mac_address\':\'%s\', \'ip_address\':%s, \'host_name\':\'%s\', \'description\':\'%s\'}' % (self.mac_address, self.ip_address, self.host_name, self.description )
	def __unicode__(self):
		return u'%s-%s-%s' % (self.mac_address, str(IPAddress(self.ip_address)), self.host_name )

	
class DHCP_ip_pool(models.Model):						#DHCP IP ADDRESS POOL MODEL
	ip_first	= models.IntegerField('IP range from')			#DHCP address range
	ip_last		= models.IntegerField('IP range to')			#DHCP address range
	is_ipv6 	= models.BooleanField()					#DHCP bool check IP version 6
	description 	= models.TextField('Description',blank=True, null=True)	#DHCP IP pool description
	time_created 	= models.DateTimeField()				#DHCP time IP pool creation time
	time_modified	= models.DateTimeField()				#DHCP time IP pool modification time
	#is_active 	= models.BooleanField()					#DHCP IP pool activation - to delete
	#IP_pool1
	#IP_pool2
	def LogRepresentation(self):
		return u'{\'ip_first\':%s, \'ip_last\':%s,\'description\':\'%s\'}' % (self.ip_first, self.ip_last,self.description )
	def __unicode__(self):
		return u'%s %s %s' % (str(IPAddress(self.ip_first)), str(IPAddress(self.ip_last)), self.time_created )

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

