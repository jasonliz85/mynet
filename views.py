from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import datetime
from subnets.AccessControl import get_netgroups_managed_by_user, get_address_blocks_managed_by, get_dns_patterns_managed_by
import pickle
	
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
	#Get user information
	userInfo["username"] = request.user.username
	userInfo["first_name"] = request.user.first_name
	userInfo["last_name"] = request.user.last_name
	Groups = request.user.groups.all().values()
	#Get and Set Network Resources, IP Subnet and DNS Expressions
	NetworkResources 	= get_netgroups_managed_by_user(request.user)
	IPRanges 			= get_address_blocks_managed_by(request.user)
	DNSExpressions 		= get_dns_patterns_managed_by(request.user)
	#return
	return render_to_response('qmul_main.html', {'userInfo': userInfo, 'Groups':Groups, 'NetworkResources':NetworkResources, 'IPRanges':IPRanges,'DNSExpressions':DNSExpressions })
@login_required
def dhcp_page(request):
	return render_to_response('qmul_dhcp.html', {})
def dns_page(request):
	return render_to_response('qmul_dns.html', {})
def permission_error(request):
	return render_to_response('qmul_permission_error.html', {})
def record_error(request):
	return render_to_response('qmul_permission_error.html', {})
#-----Testing- To delete ----------
def time_info(request):
	dns_timing = {}
	dns_timing['total'] = request.session["_dns_list_total_timing"]
	dns_timing['view'] = request.session["_dns_list_view_timing"]
	dns_timing['template'] = request.session["_dns_list_template_timing"]
	dns_timing['t1t2'] = request.session["_dns_list_t1t2_timing"]
	dns_timing['t2t3'] = request.session["_dns_list_t2t3_timing"]
	return render_to_response('info.html', {'dns_timing':dns_timing})
#----------------------------------
###########################################################################################
###########################################################################################
###########################################################################################
