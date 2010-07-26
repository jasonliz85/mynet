from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import Context
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from IPy import IP
import datetime

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
	userInfo["group_list"] = request.user.groups.all()
	return render_to_response('qmul_main.html', {'userInfo': userInfo})
@login_required
def history(request):
	historyMessage = {}
	#historyMessage["message"] = request.user.message_get.all() try actions
	return render_to_response('qmul_history.html', {"hMessage": historyMessage})
@login_required
def dhcp_page(request):
	return render_to_response('qmul_dhcp.html', {})
def dns_page(request):
	return render_to_response('qmul_dns.html', {})



