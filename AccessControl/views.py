from django.db.models import Q
from django.db import IntegrityError
from mynet.AccessControl.models import *
from netaddr import IPAddress, IPNetwork
import datetime, re

__all__ = [	'get_netgroups_managed_by_user',
		'get_dns_patterns_managed_by',
		'get_address_blocks_managed_by',
		'get_subnet_from_ip',
		'is_ipaddress_in_netresource',
		'is_name_in_netresource', 
		'get_permissions_to_session', 
		'add_permissions_to_session']
###############################################################################
############################# Useful Functions ################################
###############################################################################
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

def get_subnet_from_ip(user_obj, ip):
	"""
	Returns a subnet (as a string) that an ip belongs to. Returns an empty string if no subnets can be found.
	"""
	subnet = ''
	if not hasattr(user_obj, '_address_blocks') or True:
		address_blocks = [] #list containing all address blocks the user is allowed to change
		for netgroup in get_netgroups_managed_by_user(user_obj):
			for addressblock in netgroup.address_blocks.all():
				sn = IPNetwork(str(addressblock))
				if int(ip) > int(sn[0]) and int(ip) < int(sn[-1]):
					subnet = str(sn)
					
	return subnet

def add_permissions_to_session(request):
	"""
	Add Network Resource Name, IP Blocks (IP Address Ranges), and DNS Expressions to Django session
	"""
	#Network Resources	 	
	request.session['network_resources'] 	= get_netgroups_managed_by_user(request.user)
	#IP Ranges
	request.session['ip_blocks'] 		= get_address_blocks_managed_by(request.user)
	#DNS Expressions	 
	request.session['dns_expressions'] 	= get_dns_patterns_managed_by(request.user)	
	
	return

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
	It assumes the input ip address is of type IPAddress.
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

def is_name_in_netresource(request, dns_name):
	"""
	returns true if the input machine name (dns_name) the dns expression specified in the user's session, else returns false. 
	"""
	#[blank1, blank2, dns_expressions] = get_permissions_to_session(request)
	dns_expressions  = request.session['dns_expressions']
	has_permission = False
	#for each dns expression in all dns expressions in the list...
	for expression in range(len(dns_expressions)):
		#...modify expression...
		temp = '\S' + str(dns_expressions[expression])
		dns_re = re.compile(temp)
		#... and check if matches with input dns_name
		if re.match(dns_re, dns_name):
			has_permission = True
			break

	return has_permission

def add_ip_subnet(values):
	'''
	This function adds an ip subnet to the model ip_subnet. If record.save is not unique, return as Error = True
	'''
	Error = ''
##	new_subnet = ip_subnet(	ip_value = values['ip_value'],
##							vlan	= values['vlan'],
##							description = values['description']
##							)
#	
#	try:
#		p, created = ip_subnet.objects.get_or_create(	ip_value 	= values['ip_value'],
#														vlan		= values['vlan'],
#														description = values['description']
#														)
#	print "About to try: ", values['ip_value']
	new_subnet = ip_subnet(	ip_network = IPNetwork(values['ip_value']),
							vlan	= values['vlan'],
							description = values['description']
							)
	try:
		new_subnet.save()
	except Exception, e:
		return True, e
#	new_subnet.save()
#	try:
##		p, created = ip_subnet.objects.get_or_create(	ip_network 	= IPNetwork(values['ip_value']),
#		net = IPNetwork(values['ip_value'])
#		print "Net value: ", net
#		p, created = ip_subnet.objects.get_or_create(   ip_network  = net,
#														vlan		= values['vlan'],
#														description = values['description']
#	 												)
#		print "Tried: ", values['ip_value'] 										
#	except Exception, e:
#		print "Exception found: ", values['ip_value']
#		if isinstance(e, IntegrityError):
#			Error = 'IP subnet is not unique'
#			return True, Error
#		elif isinstance(e, ValueError):
#			Error = 'IP subnet (string), vlan (integer) or Description (text) are of the wrong type.'
#			return True, Error
#		print values['ip_value']
		#raise exceptions.AttributeError('')
#		Error = 'IP subnet is not unique'
#		print Error
#		return True, Error
#	except ValueError:
#		Error = 'IP subnet (string), vlan (integer) or Description (text) are of the wrong type.'
#		print Error
#		return True, Error
	
	return False, Error
