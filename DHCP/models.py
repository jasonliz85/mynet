from django.db import models
from netaddr import IPAddress

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
