from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import datetime
from AccessControl.models import get_netgroups_managed_by_user, get_address_blocks_managed_by, get_dns_patterns_managed_by#add_permissions_to_session, get_permissions_to_session


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

	return render_to_response('qmul_main.html', {'userInfo': userInfo, 'Groups':Groups, 'NetworkResources':NetworkResources, 'IPRanges':IPRanges,'DNSExpressions':DNSExpressions })

@login_required
def dhcp_page(request):
	return render_to_response('qmul_dhcp.html', {})
def dns_page(request):
	return render_to_response('qmul_dns.html', {})
	
###########################################################################################
###########################################################################################
###########################################################################################
