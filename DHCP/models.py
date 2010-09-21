from django.db import models
from mynet.DHCP.manager import *
from netaddr import IPAddress, IPNetwork
#from mynet.AccessControl.views import is_ipaddress_in_netresource
from django.db.models import Q
import NetaddrCustomizations.models
		
class DHCP_machine(models.Model): 						#DHCP MACHINE REGISTRATION MODEL
	mac_address	= models.CharField('MAC address', max_length = 40)	#DHCP MAC address
	ip_address	= NetaddrCustomizations.models.NetaddrIPAddressField('IP Address')
	#ip_address	= models.IntegerField('IP address')			#DHCP IP address 
	host_name	= models.CharField('Host name', max_length = 63)	#DHCP Host name
	is_ipv6 	= models.BooleanField()					#DHCP bool check IP version 6
	description 	= models.TextField('Description', blank=True, null=True)	#DHCP machine description of machine (optional)
	time_created 	= models.DateTimeField()				#DHCP machine registration creation time	
	time_modified	= models.DateTimeField()				#DHCP machine registration modification time	
	objects 	= MachineManager()
	def LogRepresentation(self):
		return u'{\'mac_address\':\'%s\', \'ip_address\':%s, \'host_name\':\'%s\', \'description\':\'%s\'}' % (self.mac_address, self.ip_address, self.host_name, self.description )
	def __unicode__(self):
		return u'%s-%s-%s' % (self.mac_address, str(IPAddress(self.ip_address)), self.host_name )
	class Meta:
        	ordering = ['ip_address', 'is_ipv6']

class DHCP_ip_pool(models.Model):						#DHCP IP ADDRESS POOL MODEL
	ip_first	= NetaddrCustomizations.models.NetaddrIPAddressField('IP range from')
	ip_last		= NetaddrCustomizations.models.NetaddrIPAddressField('IP range to')
	#ip_first	= models.IntegerField('IP range from')			#DHCP address range
	#ip_last	= models.IntegerField('IP range to')			#DHCP address range
	is_ipv6 	= models.BooleanField()					#DHCP bool check IP version 6
	description 	= models.TextField('Description',blank=True, null=True)	#DHCP IP pool description
	time_created 	= models.DateTimeField()				#DHCP time IP pool creation time
	time_modified	= models.DateTimeField()				#DHCP time IP pool modification time
	objects		= IPPoolManager()
	def LogRepresentation(self):
		return u'{\'ip_first\':%s, \'ip_last\':%s,\'description\':\'%s\'}' % (self.ip_first, self.ip_last,self.description )
	def __unicode__(self):
		return u'%s %s %s' % (str(IPAddress(self.ip_first)), str(IPAddress(self.ip_last)), self.time_created )
	class Meta:
        	ordering = ['ip_first', 'is_ipv6']
        	
def dhcp_permission_check(request, ip_address1, ip_address2, is_dhcp_pool):
	"""
	This function checks whether a dhcp address (ipaddress1) can be created based on the user's network resource group.
	If is_dhcp_pool is True, this function will check if both input ip addresses (ip_address1 and ip_address2) are within
	the same network resource block. In both cases, if permitted then the function return True.
	"""
	has_permission = False
	custom_errors = ''#list()
	msg1 = 'Both IP addresses must be within your allowed resource group, please check and try again.'
	msg2 = 'The starting IP address, '#'You are not allowed to add this \'start IP address\', it is not part of your network resource group.'
	msg3 = 'The ending IP address, '#'You are not allowed to add this \'end IP address\', it is not part of your network resource group.'
	msg4 = ', is not permitted. '
	msg5 = 'You are not allowed to add this IP Address, it is not part of your network resource group.'
	msg6 = 'Starting and ending IP addresses are not permitted. '
	msg7 = 'Starting and ending addresses must be in the same subnet. '
	[check1, ip_block1]  = is_ipaddress_in_netresource(request, ip_address1)
	
	#
	if is_dhcp_pool:
		[check2, ip_block2]  = is_ipaddress_in_netresource(request, ip_address2)
	else:
		check2 = True
		ip_block2 = ip_block1
		
	if not check1 or not check2 or not ip_block1 == ip_block2:	
		#ip pools
		if not ip_block1 == ip_block2:
			if not check1:
				custom_errors = msg2 + str(IPAddress(ip_address1)) + msg4 + msg1
			elif not check2:
				custom_errors = msg3 + str(IPAddress(ip_address2)) + msg4 + msg1
			else:
				custom_errors = msg7 + msg1
		elif not check1 and not check2:
			custom_errors = msg6 + msg1
		#machine names
		elif not is_dhcp_pool:
			custom_errors = msg5
			
	else:
		has_permission = True

	return has_permission, custom_errors
