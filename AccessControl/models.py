from django.db import models

from django.contrib.auth.models import Group

class DNS_names(models.Model):							#DNS NAMING MODEL
	machine_name 	= models.CharField('DNS name', max_length = 30)		#DNS name regular expression
	ip_pair		= models.IntegerField('IP address')			#DNs ip address pair
	dns_type	= models.CharField('Type', max_length = 3 )		#DNS type
	description 	= models.TextField('Description', blank=True, null=True)#DNS name description
	is_ipv6 	= models.BooleanField()					#DNS bool check IP version 6
	time_created 	= models.DateTimeField()				#DNS name creation time
	is_active 	= models.BooleanField()					#DNS reg active

	def LogRepresentation(self):
		return u'{\'machine_name\':\'%s\', \'ip_pair\':%s, \'dns_type\':\'%s\', \'description\':\'%s\'}' % (self.machine_name, self.ip_pair, self.dns_type, self.description )
	def __unicode__(self):
		return u'\'machine_name\':\'%s\',\'ip_pair\':\'%s\',\'is_ipv6\':\'%s\',\'dns_type\':\'%s\',\'description\':\'%s\''% (self.machine_name, str(IPAddress(self.ip_pair)), self.is_ipv6, self.dns_type, self.description)
	class Meta:
        	ordering = ['ip_pair','dns_type']

class DHCP_machine(models.Model):						#DHCP MACHINE REGISTRATION MODEL
	MAC_pair	= models.CharField('MAC address', max_length = 40)	#DHCP MAC address 
	IP_pair		= models.IntegerField('IP address')			#DHCP IP address 
	PC_pair		= models.CharField('PC name', max_length = 12)		#DHCP PC name
	description 	= models.TextField('Description',blank=True, null=True)	#DHCP machine description of machine (optional)
	time_created 	= models.DateTimeField()				#DHCP machine registration creation time	
	def LogRepresentation(self):
		return u'{\'MAC_pair\':\'%s\', \'IP_pair\':%s, \'PC_pair\':\'%s\', \'description\':\'%s\'}' % (self.MAC_pair, self.IP_pair, self.PC_pair, self.description )
	def __unicode__(self):
		return u'%s-%s-%s' % (self.MAC_pair, str(IPAddress(self.IP_pair)), self.PC_pair )

	
class DHCP_ip_pool(models.Model):						#DHCP IP ADDRESS POOL MODEL
	IP_pool1	= models.IntegerField('IP range from')			#DHCP address range
	IP_pool2	= models.IntegerField('IP range to')			#DHCP address range
	description 	= models.TextField('Description',blank=True, null=True)	#DHCP IP pool description
	time_created 	= models.DateTimeField()				#DHCP time IP pool creation time
	is_ipv6 	= models.BooleanField()					#DHCP bool check IP version 6
	is_active 	= models.BooleanField()					#DHCP IP pool activation
	def LogRepresentation(self):
		return u'{\'IP_pool1\':%s, \'IP_pool2\':%s,\'description\':\'%s\'}' % (self.IP_pool1, self.IP_pool2,self.description )
	def __unicode__(self):
		return u'%s %s %s' % (str(IPAddress(self.IP_pool1)), str(IPAddress(self.IP_pool2)), self.time_created )

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
		print 'Starting loops'
		for g in user_obj.groups.all():
			print 'Group', g
			for ng in g.netgroup_set.all():
				print 'NetGroup', ng 
				if ng not in netgroup_cache: netgroup_cache.append(ng)
		user_obj._netgroup_cache = netgroup_cache
	return	user_obj._netgroup_cache

def get_address_blocks_managed_by(user_obj):
	"""
	Returns a list of IP address block objects which the user can manage
	"""
	if not hasattr(user_obj, '_address_blocks') or True:
		address_blocks = []
		for ng in get_netgroups_managed_by_user(user_obj):
			for ab in ng.address_blocks.all():
				if ab not in address_blocks: address_blocks.append(ab)
		user_obj._address_blocks = address_blocks
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

