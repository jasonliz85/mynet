from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import Context
from django.http import HttpResponse
import datetime

def login(request):
	return render_to_response('qmul_login.html', {})

def home(request):
	return render_to_response('qmul_main.html', {})

def dns_page(request):
	return render_to_response('qmul_dns.html', {})

def dns_page_addname(request):
	return render_to_response('qmul_dns_addname.html', {})

def dhcp_page(request):
	return render_to_response('qmul_dhcp.html', {})


