from django.db import models
from django.db.models import Q
from mynet.AccessControl.models import get_subnet_from_ip
from netaddr import *

def get_permissions_to_session(request):
	"""
	returns [Network Resource Name, IP Blocks (IP Address Ranges), DNS Expressions] from the Django session
	"""
	net_res = request.session['network_resources']
	ip_ran  = request.session['ip_blocks']
	dns_exp = request.session['dns_expressions']
	
	return net_res, ip_ran, dns_exp

def is_ipaddress_in_netresource(request, ip_address):	
	"""
	returns true if the input ip address (ip_address) is within the ip blocks specified in the user's session, else returns false. 
	It assumes the input ip address is in integer form.
	"""
	#[blank1, ip_blocks, blank2] = get_permissions_to_session(request)
	ip_blocks = request.session['ip_blocks']
	ip_block_str = ''
	has_permission = False
	#for each ip address block in all ip address blocks in the list...
	for block in range(len(ip_blocks)):
		ip_block = IPNetwork(str(ip_blocks[block]))
		#...check if ip_address is within range
		if int(ip_address) < int(ip_block[-1]) and int(ip_address) > int(ip_block[0]):
			has_permission = True			
			ip_block_str = str(ip_blocks[block])
			break

	return has_permission, ip_block_str
	
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
		subnet = IPNetwork(subnet)
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
	def get_permitted_records(self, request):
		"""
		This function returns a queryset from the model DHCP_macgroupshine . The returned results are filtered by permitted
		ip_blocks that the user is able to access. 
		"""
		#Get network groups, ip blocks and dns expressions which the user has permission to control
		[net_groups, ip_blocks, dns_exprs] = get_permissions_to_session(request)
	
		empty_find = True
		for block in range(len(ip_blocks)):
			ip_block = IPNetwork(str(ip_blocks[block]))
			ip_filter_upper = Q(ip_address__lt = ip_block[-1])
			ip_filter_lower = Q(ip_address__gt = ip_block[0])
			#filter the ip block
			finds = self.filter( ip_filter_upper, ip_filter_lower )
			if block == 0:
				total_ip_finds = finds
				if len(finds) == 0:
					empty_find = True
				else:
					empty_find = False
			else:
				if len(finds) == 0:
					if empty_find:
						empty_find = True	
				else:
					if empty_find:
						total_ip_finds = finds
						empty_find = False
					else:
						total_ip_finds = finds|total_ip_finds

		if not empty_find:
			permitted_record = total_ip_finds
		else:
			permitted_record = list()
					
		return permitted_record
	
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
		subnet1 = IPNetwork(subnet1)
		subnet2 = IPNetwork(subnet2)
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
		
	def get_permitted_records(self, request):
		"""
		This function returns a queryset from the model DHCP_ip_pool . The returned results are filtered by permitted
		ip_blocks that the user is able to access. 
		"""
		#Get network groups, ip blocks and dns expressions which the user has permission to control
		[net_groups, ip_blocks, dns_exprs] = get_permissions_to_session(request)
	
		empty_find = True
		for block in range(len(ip_blocks)):
			ip_block = IPNetwork(str(ip_blocks[block]))
			ip_first_upper	= Q(ip_first__lt = ip_block[-1])
			ip_first_lower 	= Q(ip_first__gt = ip_block[0])
			ip_last_upper 	= Q(ip_last__lt = ip_block[-1])
			ip_last_lower 	= Q(ip_last__gt = ip_block[0])
			#filter the ip block
			finds = self.filter((ip_first_upper & ip_first_lower) & (ip_last_lower & ip_last_upper)) #& (ip_last_lower, ip_last_upper)
			if block == 0:
				total_ip_finds = finds
				if len(finds) == 0:
					empty_find = True
				else:
					empty_find = False
			else:
				if len(finds) == 0:
					if empty_find:
						empty_find = True	
				else:
					if empty_find:
						total_ip_finds = finds
						empty_find = False
					else:
						total_ip_finds = finds|total_ip_finds

		if not empty_find:
			permitted_record = total_ip_finds
		else:
			permitted_record = list()
					
		return permitted_record
