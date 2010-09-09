from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from AccessControl.views import add_permissions_to_session, get_permissions_to_session

import datetime
from netaddr import *

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
	
	#is_ipaddress_in_netresource(request, int(IPAddress('192.0.2.1')))

	return render_to_response('qmul_main.html', {'userInfo': userInfo, 'Groups':Groups, 'NetworkResources':NetworkResources, 'IPRanges':IPRanges,'DNSExpressions':DNSExpressions })

@login_required
def dhcp_page(request):
	return render_to_response('qmul_dhcp.html', {})
def dns_page(request):
	return render_to_response('qmul_dns.html', {})
	
###########################################################################################
###########################################################################################
###########################################################################################
