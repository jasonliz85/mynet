from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict
#model imports
from mynet.AccessControl.models import *
from mynet.HistoryLog.models import *
from mynet.DNS.models import *
from mynet.DHCP.models import *
#form imports
from mynet.AccessControl.forms import *
#view imports
from mynet.views import *
from mynet.HistoryLog.views import *

from django.db.models import Q

from netaddr import *
import datetime, re

def add_permissions_to_session(request):
	"""
	Add Network Resource Name, IP Blocks (IP Address Ranges), and DNS Expressions to Django session
	"""
	#Network Resources	 	
	request.session['network_resources'] = get_netgroups_managed_by_user(request.user)
	#IP Ranges
	request.session['ip_blocks'] = get_address_blocks_managed_by(request.user)
	#DNS Expressions	 
	request.session['dns_expressions'] = get_dns_patterns_managed_by(request.user)
	
	return
def is_ipaddress_in_netresource(request, ip_address):	
	"""
	returns true if the input ip address (ip_address) is within the ip blocks specified in the user's session, else returns false. 
	It assumes the input ip address is in integer form.
	"""
	ip_blocks  = request.session['ip_blocks']
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

def get_permissions_to_session(request):
	"""
	returns [Network Resource Name, IP Blocks (IP Address Ranges), DNS Expressions] from the Django session
	"""
	net_res = request.session['network_resources']
	ip_ran  = request.session['ip_blocks']
	dns_exp = request.session['dns_expressions']
	
	return net_res, ip_ran, dns_exp
	
def dns_permission_check(request, ip_address, name, dns_typ):
	"""
	This function checks the name, ipaddress and dns type to see the record is allowed to be created. There are three check, stated below:
		bi-directional - two checks on each record is needed | permission for both ip address and machine name
		address to name - check only pefrom mynet.DNS.models import *rmission for ip address
		name to address - check only permisiion for machine name
	"""
	has_permission = False	
	custom_errors = list()
	message1 = 'You are not allowed to add this IP Address, it is not part of your network resource group.'
	message2 = 'You are not allowed to add this Machine Name, it is not part of your network resource group.'
	[check1, blank] = is_ipaddress_in_netresource(request, ip_address)
	check2 = is_name_in_netresource(request, name)
	if dns_typ == '1BD':
		if check1 == True and check2  == True:
			has_permission = True
		if not check1:
			custom_errors.append({'error':True, 'message': message1})
		if not check2:
			custom_errors.append({'error':True, 'message': message2})
	elif dns_typ == '2NA':
		if check2 == True:
			has_permission = True
		if not check2:
			custom_errors.append({'error':True, 'message': message2})
	else:
		if check1 == True:
			has_permission = True
		if not check1:
			custom_errors.append({'error':True, 'message': message1})	
	
	return has_permission, custom_errors

def dhcp_permission_check(request, ip_address1, ip_address2, is_dhcp_pool):
	"""
	This function checks whether a dhcp address (ipaddress1) can be created based on the user's network resource group.
	If is_dhcp_pool is True, this function will check if both input ip addresses (ip_address1 and ip_address2) are within
	the same network resource block. In both cases, if permitted then the function return True.
	"""
	has_permission = False
	custom_errors = list()
	msg1 = 'Both IP addresses must be within your allowed resource group, please check and try again.'
	msg2 = ' The starting IP address is invalid.'#'You are not allowed to add this \'start IP address\', it is not part of your network resource group.'
	msg3 = ' The ending IP address is invalid.'#'You are not allowed to add this \'end IP address\', it is not part of your network resource group.'
	msg4 = 'Both IP addresses must be within the same permitted CIDR block.'
	msg5 = 'You are not allowed to add this IP Address, it is not part of your network resource group.'
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
			#custom_errors.append({'error':True, 'message': msg1})
			if not check1:
				custom_errors.append({'error':True, 'message': msg1 + msg2})
			elif not check2:
				custom_errors.append({'error':True, 'message': msg1 + msg3})
			else:
				custom_errors.append({'error':True, 'message': msg4})
		elif not check1 and not check2:
			custom_errors.append({'error':True, 'message': msg1})
		#machine names
		elif not is_dhcp_pool:
			custom_errors.append({'error':True, 'message': msg5})
			
	else:
		has_permission = True
	
	return has_permission, custom_errors

def dns_get_permited_records(request, enable_type_filter):
	"""
	This function return a queryset from the model table DNS_name. The returned results are filtered by permitted
	ip_blocks, dns_expressions and dns_type that the user is able to access. If enable_type_filter is enabled, 
	a further filtering step is applied - please see comments this function for further information.
	"""
	#Get network groups, ip blocks and dns expressions which the user has permission to control
	[net_groups, ip_blocks, dns_exprs] = get_permissions_to_session(request)
	
	#first find all the ip addresses that the user has permission to control
	empty_find = True
	for block in range(len(ip_blocks)):
		ip_block = IPNetwork(str(ip_blocks[block]))
		ip_filter_upper = Q(ip_address__lt = int(ip_block[-1]))
		ip_filter_lower = Q(ip_address__gt = int(ip_block[0]))
		#filter the ip block
		finds = DNS_name.objects.filter( ip_filter_upper, ip_filter_lower )
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
	#second, find all the dns names that the user can control
	empty_find = True
	for expression in range(len(dns_exprs)):
		dns_filter = Q(name__regex = ('\S' + str(dns_exprs[expression])))
		finds = DNS_name.objects.filter( dns_filter )
		if expression == 0:	
			total_name_finds = finds
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
					total_name_finds = finds
					empty_find = False
				else:
					total_name_finds = finds|total_name_finds
					
	if len(dns_exprs) > 0 and len(ip_blocks) > 0:
		combined_records = total_name_finds|total_ip_finds
	else:
		combined_records = list()
	#we now have a combimed result- great! we now need to filter these a bit more (assuming enable_filter_type is True)
	#so, if the type of record is:
	#bi-directional - two checks on each record is needed | permission for both ip address and machine name
	#address to name - check only permission for ip address
	#name to address - check only permisiion for machine name
	if enable_type_filter:
		type_filtered_records = list()
		for record in range(len(combined_records)):
			has_permission = False
			#dt = combined_records[record].dns_type		#dns type
			[has_permission, msg] = dns_permission_check(	request,
									combined_records[record].ip_address,
									combined_records[record].name,
									combined_records[record].dns_type)
			#checked for one of three types and checked whether the above conditions are true
			#if true, add to overall list to return
			if has_permission:
				type_filtered_records.append(combined_records[record])
		
		permitted_records = type_filtered_records
	else:
		permitted_records = combined_records
	
	return permitted_records

def dhcp_machine_get_permitted_records(request):
	"""
	This function returns a queryset from the model DHCP_machine . The returned results are filtered by permitted
	ip_blocks that the user is able to access. 
	"""
	#Get network groups, ip blocks and dns expressions which the user has permission to control
	[net_groups, ip_blocks, dns_exprs] = get_permissions_to_session(request)
	
	empty_find = True
	for block in range(len(ip_blocks)):
		ip_block = IPNetwork(str(ip_blocks[block]))
		ip_filter_upper = Q(ip_address__lt = int(ip_block[-1]))
		ip_filter_lower = Q(ip_address__gt = int(ip_block[0]))
		#filter the ip block
		finds = DHCP_machine.objects.filter( ip_filter_upper, ip_filter_lower )
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
	
def dhcp_pool_get_permitted_records(request):
	"""
	This function returns a queryset from the model DHCP_ip_pool . The returned results are filtered by permitted
	ip_blocks that the user is able to access. 
	"""
	#Get network groups, ip blocks and dns expressions which the user has permission to control
	[net_groups, ip_blocks, dns_exprs] = get_permissions_to_session(request)
	
	empty_find = True
	for block in range(len(ip_blocks)):
		ip_block = IPNetwork(str(ip_blocks[block]))
		ip_first_upper	= Q(ip_first__lt = int(ip_block[-1]))
		ip_first_lower 	= Q(ip_first__gt = int(ip_block[0]))
		ip_last_upper 	= Q(ip_last__lt = int(ip_block[-1]))
		ip_last_lower 	= Q(ip_last__gt = int(ip_block[0]))
		#filter the ip block
		finds = DHCP_ip_pool.objects.filter((ip_first_upper & ip_first_lower) & (ip_last_lower & ip_last_upper)) #& (ip_last_lower, ip_last_upper)
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


