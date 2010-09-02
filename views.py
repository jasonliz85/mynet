from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from mynet.AccessControl.models import *

import datetime
import re
from netaddr import *

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
	has_permission = False
	#for each ip address block in all ip address blocks in the list...
	for block in range(len(ip_blocks)):
		ip_block = IPNetwork(str(ip_blocks[block]))
		#...check if ip_address is within range
		if ip_address < int(ip_block[-1]) and ip_address > int(ip_block[0]):
			print "Permission allowed for ", IPAddress(ip_address), " in Network ", ip_block
			has_permission = True

	return has_permission

def is_name_in_netresource(request, dns_name):
	"""
	returns true if the input machine name (dns_name) the dns expression specified in the user's session, else returns false. 
	"""
	dns_expressions  = request.session['dns_expressions']
	has_permission = False
	print dns_expressions
	#for each dns expression in all dns expressions in the list...
	for expression in range(len(dns_expressions)):
		#...modify expression...
		temp = '\S' + str(dns_expressions[expression])
		dns_re = re.compile(temp)
		#... and check if matches with input dns_name
		if re.match(dns_re, dns_name):
			print "Machine name ", dns_name, "is allowed for expression", dns_expressions[expression]
			has_permission = True

	return has_permission

def get_permissions_to_session(request):
	"""
	returns [Network Resource Name, IP Blocks (IP Address Ranges), and DNS Expressions] from the Django session
	"""
	net_res = request.session['network_resources']
	ip_ran  = request.session['ip_blocks']
	dns_exp = request.session['dns_expressions']
	
	return net_res, ip_ran, dns_exp

def login(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)         # Correct password, and the user is marked "active"
	return HttpResponseRedirect("/home/")         # Redirect to a success page.
    else:        
        return HttpResponseRedirect("login.html") # Show an error page
        
def logout_view(request, next_page):
    auth.logout(request)		# Redirect to a success page.    
    return HttpResponseRedirect("/loggedout/")

@login_required
def home(request):
	userInfo = {}
	userInfo["username"] = request.user.username
	userInfo["first_name"] = request.user.first_name
	userInfo["last_name"] = request.user.last_name
	Groups = request.user.groups.all().values()
	
	add_permissions_to_session(request)
	[NetworkResources, IPRanges, DNSExpressions] = get_permissions_to_session(request)
	
	is_ipaddress_in_netresource(request, int(IPAddress('192.0.2.1')))

	return render_to_response('qmul_main.html', {'userInfo': userInfo, 'Groups':Groups, 'NetworkResources':NetworkResources, 'IPRanges':IPRanges,'DNSExpressions':DNSExpressions })

@login_required
def dhcp_page(request):
	return render_to_response('qmul_dhcp.html', {})
def dns_page(request):
	return render_to_response('qmul_dns.html', {})
	
###########################################################################################
###########################################################################################
###########################################################################################
