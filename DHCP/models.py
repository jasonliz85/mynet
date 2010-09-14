from django.db import models
from netaddr import IPAddress, IPNetwork
from mynet.AccessControl.models import get_subnet_from_ip

from django.db.models import Q

class MachineManager(models.Manager):
	def is_unique(self, user_obj, ip, mac, mid):
		'''
		This funtion checks whether the input mac address is unique for the subnet specfied by the input
		ip address. Returns True if unique, False otherwise. Assumes ip is the integer form of an ip addresses.
		'''
		#Algorithm
		unique = True
		unique_error = ''
		#1. find subnet belonging to ip address	(ip)	
		subnet = get_subnet_from_ip(user_obj, ip)
		if not len(subnet):
			unique = False
			unique_error = "You do not have permission to add/edit this IP address."
			return unique, unique_error
		#2. find all records that are also within this subnet
		found_records = list() 
		ip_filter_upper = Q(ip_address__lt = int(subnet[-1]))
		ip_filter_lower = Q(ip_address__gt = int(subnet[0]))
		try: 
			found_records = self.filter(ip_filter_upper, ip_filter_lower).exclude(id = mid)
		except ValueError:
			found_records = self.filter(ip_filter_upper, ip_filter_lower)
		if not len(found_records):
			return unique, unique_error
		#3. for each record that was found, check their mac address with this mac address (mac) 
		for record in found_records:
			#4. if record mac address is equal to input mac address, not unique
			if record.mac_address == mac:
				unique_error = "You cannot use this MAC Address, it has already been used for this subnet."
				unique = False
			else:
				if record.ip_address == ip:
					unique_error = "You cannot use this IP address, it has already been used for this subnet."
					unique = False
							
		return unique, unique_error
	
class IPPoolManager(models.Manager):
	def is_unique(self, user_obj, ip_f, ip_l, mid):
		'''
		This function performs a number of checks and returns true if all checks are true:
		1. ip first and last must not overlap with other ip pools within the same subnet 	#todo
		2. ip first and last must not overlap an ipaddress declared as a registered machine 	#todo
		3. ip first and last is strictly unique for this given subnet				#implemented
		Assumes ip_f and ip_l are integer forms of ip addresses
		'''
		
		unique = True
		unique_error = ''
		#Get subnet for ip_f and ip_l			
		subnet1 = get_subnet_from_ip(user_obj, ip_f)
		subnet2 = get_subnet_from_ip(user_obj, ip_l)
		if not len(subnet1) or not len(subnet2):
			unique = False
			unique_error = "You do not have permission to add/edit this IP address."
			return unique, unique_error
		elif not subnet1 == subnet2:
			unique = False
			unique_error = "You do not have permission to add/edit this IP address."
			return unique, unique_error
		#Get records associated with these addresses. 
		found_records = list() 
		ip_first_upper	= Q(ip_first__lt = int(subnet1[-1]))
		ip_first_lower 	= Q(ip_first__gt = int(subnet1[0]))
		ip_last_upper 	= Q(ip_last__lt = int(subnet1[-1]))
		ip_last_lower 	= Q(ip_last__gt = int(subnet1[0]))		
		try: 
			found_records = self.filter((ip_first_upper & ip_first_lower) & (ip_last_lower & ip_last_upper)).exclude(id = mid) 
		except ValueError:
			found_records = self.filter((ip_first_upper & ip_first_lower) & (ip_last_lower & ip_last_upper)) 
		if not len(found_records):
			return unique, unique_error
		
		# Now implement check 3
		for record in found_records:
			if record.ip_first == ip_f and record.ip_last == ip_l:
				unique_error = "This range had already been created for this subnet."
				unique = False
				break
			elif record.ip_first == ip_f:
				unique_error = "You cannot use this first IP address, it has already been used for this subnet."
				unique = False
				break
			elif record.ip_last == ip_l:
				unique_error = "You cannot use this last IP address, it has already been used for this subnet."
				unique = False
				break
							
		return unique, unique_error
		
class DHCP_machine(models.Model): 						#DHCP MACHINE REGISTRATION MODEL
	mac_address	= models.CharField('MAC address', max_length = 40)	#DHCP MAC address
	ip_address	= models.IntegerField('IP address')			#DHCP IP address 
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
        	ordering = ['ip_address']

class DHCP_ip_pool(models.Model):						#DHCP IP ADDRESS POOL MODEL
	ip_first	= models.IntegerField('IP range from')			#DHCP address range
	ip_last		= models.IntegerField('IP range to')			#DHCP address range
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
        	ordering = ['ip_first']
