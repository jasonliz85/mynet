from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import datetime
from mynet.AccessControl import get_netgroups_managed_by_user, get_address_blocks_managed_by, get_dns_patterns_managed_by#add_permissions_to_session, get_permissions_to_session
import pickle


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
	
	try:
		print request.session.__dict__
		#pickle.dumps(request.session.__dict__, pickle.HIGHEST_PROTOCOL)
		for k,value in request.session.__dict__['_session_cache'].items():
			if k in [ 'dns_expressions', 'ip_blocks']:
				continue
			print "Trying to pickle session items: ",k,value 
			x = pickle.dumps(request.session.__dict__[k], pickle.HIGHEST_PROTOCOL)
			print x
	except Exception, e:
		if isinstance(e, pickle.PicklingError):
			print "Error:%s..."% e
	return render_to_response('qmul_main.html', {'userInfo': userInfo, 'Groups':Groups, 'NetworkResources':NetworkResources, 'IPRanges':IPRanges,'DNSExpressions':DNSExpressions })
	#return render_to_response('qmul_main.html', {'userInfo': userInfo, 'Groups':Groups })
@login_required
def dhcp_page(request):
	return render_to_response('qmul_dhcp.html', {})
def dns_page(request):
	return render_to_response('qmul_dns.html', {})
def permission_error(request):
	return render_to_response('qmul_permission_error.html', {})
def record_error(request):
	return render_to_response('qmul_permission_error.html', {})
###########################################################################################
###########################################################################################
###########################################################################################
