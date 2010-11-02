from django.db.models import Q
from django.db import IntegrityError
from django.shortcuts import render_to_response
from subnets.AccessControl.models import *
from netaddr import IPAddress, IPNetwork
import datetime, re

__all__ = [	'get_netgroups_managed_by_user',
		'get_dns_patterns_managed_by',
		'get_address_blocks_managed_by',
		'get_subnet_from_ip',
		'is_ipaddress_in_netresource',
		'is_name_in_netresource', 'is_subnet_in_netresource']
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
		user_obj._address_blocks = address_blocks
	return	user_obj._address_blocks

def get_subnet_from_ip(user_obj, ip_address):
	"""
	Returns the subnet that the input ip address (IPNetwork object) belongs to. If not subnets are fount, this function will return
	an empty string.
	"""
	subnet = ''
	if not hasattr(user_obj, '_address_blocks') or True:
		address_blocks = [] #list containing all address blocks the user is allowed to change
		for netgroup in get_netgroups_managed_by_user(user_obj):
			for addressblock in netgroup.address_blocks.all():
				sn = addressblock.ip_network
				if ip_address > sn[0] and ip_address < sn[-1]:
					subnet = sn
	return subnet
	
def is_ipaddress_in_netresource(request, ip_address):	
	"""
	Returns true if the input ip address (ip_address) is within the ip blocks specified in the user's session, else returns false. 
	Function also returns the subnet which this ip address in within. This function assumes the input ip address is of type IPAddress.
	"""
	ip_blocks = get_address_blocks_managed_by(request.user)
	subnet = ''
	has_permission = False
	for block in ip_blocks: #for each ip address block in all ip address blocks in the list...
		ip_block = block.ip_network
		if ip_address < ip_block[-1] and ip_address > ip_block[0]: #...check if ip_address is within range
			has_permission = True			
			subnet = ip_block
			break
	return has_permission, subnet

def is_name_in_netresource(request, dns_name):
	"""
	Returns true if the input machine name (dns_name) the dns expression specified in the user's session, else returns false. 
	"""
	has_permission = False
	dns_expressions  = get_dns_patterns_managed_by(request.user)
	for item in dns_expressions: #for each dns expression in all dns expressions in the list...
		temp = '\S' + item.expression #...modify expression...
		if re.match(re.compile(temp), dns_name): #... and check if matches with input dns_name
			has_permission = True
			break
	return has_permission
def is_subnet_in_netresource(subnet):
	'''
	Returns True if input subnet (IPNetwork object) matches the subnets specifies in the network resource database
	'''
	is_present = False
	ip_subnets = ip_subnet.objects.all()
	for sn in ip_subnets: #for each ip address block in all ip address blocks in the list...
		if sn.ip_network == subnet: #...check if ip_address is within range
			is_present = True
			break
	return is_present
def add_ip_subnet(values):
	'''
	This function adds an ip subnet to the model ip_subnet. If record.save is not unique, return as Error = True
	'''
	new_subnet = ip_subnet(	ip_network = IPNetwork(values['ip_value']),
							vlan	= values['vlan'],
							description = values['description'] 	)
	try:
		new_subnet.save()
	except Exception, e:
		return True, e
	return False, ''
def subnets_fetch_records_txt(request):
	'''
	Returns a list of all the subnets that in the network resource subnet database
	'''
	ip_subnets = ip_subnet.objects.all()
	
	return render_to_response('qmul_subnets_all.txt', {'records': ip_subnets}, mimetype = 'text/plain')
