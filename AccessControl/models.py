from django.db import models

class test_machine(models.Model):
	MAC_pair	= models.CharField('MAC Address',max_length = 12)	#MAC address 
	IP_pair		= models.IPAddressField('IP Address')			#IP address 
	PC_pair		= models.CharField('PC Name',max_length = 12)		#PC name
	description 	= models.TextField(blank=True, null=True)		#description of machine (optional)
	def __unicode__(self):
		return u'%s-%s-%s' % (self.MAC_pair, self.IP_pair, self.PC_pair)
		
class DNS_expr(models.Model):
	expression 	= models.CharField('expression', max_length = 30)	#DNS name regular expression

class DNS_ipval(models.Model):
	ip_value	= models.CharField('name', max_length = 30)		#DNS ip address expression
			
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
		return u'%s-%s-%s' % (self.machine_name, self.is_active, self.time_created)
	
	class Meta:
        	ordering = ['ip_pair','dns_type']


class DHCP_machine(models.Model):						#DHCP MACHINE REGISTRATION MODEL
	MAC_pair	= models.CharField('MAC Address',max_length = 12)	#DHCP MAC address 
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

