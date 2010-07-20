from django.db import models

class test_machine(models.Model):
	MAC_pair	= models.CharField('MAC Address',max_length = 12)	#MAC address 
	IP_pair		= models.IPAddressField('IP Address')			#IP address 
	PC_pair		= models.CharField('PC Name',max_length = 12)		#PC name
	description 	= models.TextField(blank=True, null=True)		#description of machine (optional)
	def __unicode__(self):
		return u'%s-%s-%s' % (self.MAC_pair, self.IP_pair, self.PC_pair)
		
class DNS_names(models.Model):							#DNS NAMING MODEL
	DNS_expression 	= models.CharField('DNS name',max_length = 30)		#DNS name regular expression
	time_created 	= models.DateTimeField()				#DNS name creation time
	time_deleted 	= models.DateTimeField(blank=True, null=True)		#DNS name deletion time
	time_modified	= models.DateTimeField(blank=True, null=True)		#DNS name registration deletion time
	description 	= models.TextField(blank=True, null=True)		#DNS name description
	def __unicode__(self):
		return u'%s-%s-%s' % (self.DNS_expression, self.time_created)

class DHCP_machine(models.Model):						#DHCP MACHINE REGISTRATION MODEL
	MAC_pair	= models.CharField('MAC Address',max_length = 12)	#DHCP MAC address 
	IP_pair		= models.IPAddressField('IP Address')			#DHCP IP address 
	PC_pair		= models.CharField('PC Name',max_length = 12)		#DHCP PC name
	time_created 	= models.DateTimeField()				#DHCP machine registration creation time
	time_deleted 	= models.DateTimeField(blank=True, null=True)		#DHCP machine registration deletion time
	description 	= models.TextField(blank=True, null=True)		#DHCP machine description of machine (optional)
	#to add date_modified
	#to add global_machine_number unique ??
	#to add belongs_to_group
	def __unicode__(self):
		return u'%s-%s-%s %s, %s' % (self.MAC_pair, self.IP_pair, self.PC_pair, self.time_created, self.time_deleted )


