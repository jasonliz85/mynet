from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import datetime
from subnets.AccessControl import get_netgroups_managed_by_user, get_address_blocks_managed_by, get_dns_patterns_managed_by
import pickle
import re

def convert_normalised_to_easy_view(pattern_string):
	meta_pattern = r'^\^\(\[\^\.]\+\\.\)\*(([^.]+\.)*[^.]+)\$$'
	compiled_meta_pattern = re.compile(meta_pattern)
	match = re.match(compiled_meta_pattern, pattern_string)
	if match:
		suffix_pattern = match.group(1)
		domain_suffix = re.sub(r'\\\.', '.', suffix_pattern)
	else:
		domain_suffix = False
	return domain_suffix
def login(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        if auth.login(request, user):        # Correct password, and the user is marked "active"
			response = HttpResponseRedirect("/home/")         # Redirect to a success page.
    else:        
        response = HttpResponseRedirect("login.html") # Show an error page
    return response 
    
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
	simple_expresssions = []
	for dns_expr in DNSExpressions:
		result = convert_normalised_to_easy_view(dns_expr.expression)
		if not result:
			dns_expr.complex_expression = dns_expr.expression
		else:
			dns_expr.simple_expresssion = result
	context = Context({'userInfo': userInfo,
						'Groups':Groups, 
						'NetworkResources':NetworkResources, 
						'IPRanges':IPRanges,
						'DNSExpressions':DNSExpressions,
						'simple_expresssions':simple_expresssions })
	return render_to_response('qmul_main.html', context, context_instance=RequestContext(request))
	
@login_required
def dhcp_page(request):
	return render_to_response('qmul_dhcp.html', {}, context_instance=RequestContext(request))
@login_required
def dns_page(request):
	return render_to_response('qmul_dns.html', {}, context_instance=RequestContext(request))
@login_required
def importexport_main(request):
	return render_to_response('qmul_importexport_main.html', {}, context_instance=RequestContext(request))
def permission_error(request):
	return render_to_response('qmul_permission_error.html', {}, context_instance=RequestContext(request))
def record_error(request):
	return render_to_response('qmul_norecord_error.html', {}, context_instance=RequestContext(request))
def information_main(request):
	information_page = request.GET.get('info', 'import')
	info_type = request.GET.get('type', 'dns')
	if information_page == 'import':
		response = render_to_response('qmul_import_info.html', {'type':info_type}, context_instance=RequestContext(request))
	else:	
		response = render_to_response('qmul_information_main.html', context_instance=RequestContext(request))
	return response
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
