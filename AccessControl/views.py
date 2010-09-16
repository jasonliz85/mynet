from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict
#model imports
from mynet.AccessControl.models import *
from mynet.HistoryLog.models import *
#from mynet.DHCP.models import *

#view imports
from mynet.HistoryLog.views import *

from django.db.models import Q

from netaddr import *
import datetime, re
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

def get_subnet_from_ip(user_obj, ip):
	"""
	"""
	subnet = ''
	if not hasattr(user_obj, '_address_blocks') or True:
		address_blocks = [] #list containing all address blocks the user is allowed to change
		for netgroup in get_netgroups_managed_by_user(user_obj):
			for addressblock in netgroup.address_blocks.all():
				sn = IPNetwork(str(addressblock))
				if ip > int(sn[0]) and ip < int(sn[-1]):
					subnet = sn
	return subnet
	
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
		if ip_address < int(ip_block[-1]) and ip_address > int(ip_block[0]):
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
	
