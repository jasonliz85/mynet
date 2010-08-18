from django.db import models

from django.contrib.auth.models import Group

class test_machine(models.Model):
	MAC_pair	= models.CharField('MAC Address',max_length = 12)	#MAC address 
	IP_pair		= models.IPAddressField('IP Address')			#IP address 
	PC_pair		= models.CharField('PC Name',max_length = 12)		#PC name
	description 	= models.TextField(blank=True, null=True)		#description of machine (optional)
	def __unicode__(self):
		return u'%s-%s-%s' % (self.MAC_pair, self.IP_pair, self.PC_pair)
		
		
class DNS_names(models.Model):							#DNS NAMING MODEL
	machine_name 	= models.CharField('DNS name', max_length = 30)		#DNS name regular expression
	ip_pair		= models.CharField('IP Address', max_length = 40)	#DNs ip address pair
#	TYPE_CHOICES = ( 
#				(1, 'BD'), 	# Bi directional
#		                (2, 'NA'), 	# Machine name to IP address
#		       	        (3, 'AN'), 	# IP address to Machine name
#			)
	dns_type	= models.CharField(max_length = 3 )	#DNS type
	is_active 	= models.BooleanField()					#DNS reg active
	is_ipv6 	= models.BooleanField()					#DNS bool check IP version 6
	time_created 	= models.DateTimeField()				#DNS name creation time
	time_deleted 	= models.DateTimeField(blank=True, null=True)		#DNS name deletion time
	time_modified	= models.DateTimeField(blank=True, null=True)		#DNS name registration deletion time
	description 	= models.TextField(blank=True, null=True)		#DNS name description

	def __unicode__(self):
		return u'\'machine_name\':\'%s\',\'ip_pair\':\'%s\',\'is_ipv6\':\'%s\',\'dns_type\':\'%s\',\'description\':\'%s\''% (self.machine_name, self.ip_pair, self.is_ipv6, self.dns_type, self.description)
		#return u'%s-%s-%s' % (self.machine_name, self.is_active, self.time_created)
	
	class Meta:
        	ordering = ['ip_pair','dns_type']


class DHCP_machine(models.Model):						#DHCP MACHINE REGISTRATION MODEL
	MAC_pair	= models.CharField('MAC Address',max_length = 40)	#DHCP MAC address 
	IP_pair		= models.CharField('IP Address', max_length = 40)	#DHCP IP address 
	PC_pair		= models.CharField('PC Name',max_length = 12)		#DHCP PC name
#add	is_ipv6 	= models.BooleanField()					#DNS bool check IP version 6
	time_created 	= models.DateTimeField()				#DHCP machine registration creation time
	time_deleted 	= models.DateTimeField(blank=True, null=True)		#DHCP machine registration deletion time
	time_modified 	= models.DateTimeField(blank=True, null=True)		#DHCP machine registration modification time
	description 	= models.TextField(blank=True, null=True)		#DHCP machine description of machine (optional)
	#to add belongs_to_group ??
	#to add active
	#to add bool_is_IPv6
	def __unicode__(self):
		return u'%s-%s-%s %s, %s' % (self.MAC_pair, self.IP_pair, self.PC_pair, self.time_created, self.time_deleted )

class DHCP_ip_pool(models.Model):						#DHCP IP ADDRESS POOL MODEL
	IP_pool1	= models.CharField('IP Range1', max_length = 40 )	#DHCP address range
	IP_pool2	= models.CharField('IP Range2', max_length = 40 )	#DHCP address range
	is_active 	= models.BooleanField()					#DHCP IP pool activation
	is_ipv6 	= models.BooleanField()					#DHCP bool check IP version 6
	time_created 	= models.DateTimeField()				#DHCP time IP pool creation time
	time_deleted 	= models.DateTimeField(blank=True, null=True)		#DHCP time IP pool deletion time
	time_modified 	= models.DateTimeField(blank=True, null=True)		#DHCP time IP pool modification time
	description 	= models.TextField(blank=True, null=True)		#DHCP IP pool description
	def __unicode__(self):
		return u'%s %s %s %s' % (self.IP_pool, self.is_active, self.time_created, self.time_deleted )

# ---- #
class DNS_expr(models.Model):
	expression 	= models.CharField('expression', max_length = 100, unique=True)	#DNS name regular expression
	def __unicode__(self):
		return self.expression

class DNS_ipval(models.Model):
	ip_value	= models.CharField('name', max_length = 100, unique=True)		#DNS ip address expression
	def __unicode__(self):
		return self.ip_value
	
class NetGroup(models.Model):
	name		= models.CharField('Network Resource Group name', max_length=40, unique=True)
	managed_by	= models.ManyToManyField(Group, blank=True)
	address_blocks	= models.ManyToManyField(DNS_ipval, blank=True)
	dns_patterns	= models.ManyToManyField(DNS_expr, blank=True)	
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

def get_address_blocks_namaged_by(user_obj):
	"""
	Returns a list of IP address block objects which the user can manage
	"""
	if not hasattr(user_obj, '_address_blocks') or True:
		address_blocks = []
		for ng in get_netgroups_managed_by_user(user_obj):
			for ab in ng.address_blocks.all():
				if an not in address_blocks: address_blocks.append(ab)
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
				if dp not in address_blocks: dns_patterns.append(dp)
		user_obj._dns_patterns = dns_patterns
	return	user_obj._dns_patterns

