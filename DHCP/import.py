from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from subnets.DHCP.models import *
from subnets.DHCP.forms import UploadFileForm
from subnets.AccessControl.views import get_address_blocks_managed_by, get_dns_patterns_managed_by
from django.contrib.auth.decorators import login_required
from netaddr import IPAddress
import re

@login_required
def import_dhcp(request):
	'''
	Import dhcp functional page and form. Passes file (specified by the user) to handle_uploaded_file function and deals 
	approprietly with the response.
	'''
	if request.user.is_staff:
		if request.method == 'POST':
			form = UploadFileForm(request.POST, request.FILES)
			if form.is_valid():
				log, error = handle_uploaded_file(request, request.FILES['file'])
				pageContext = {'type': 'DHCP', 'error': error['is_error'], 'errormessage':error['Msg'] , 'errortype':error['Type'], 'log': log}
				response = render_to_response('qmul_import_result.html', pageContext)
			else:
				form = UploadFileForm()
				subnets = get_address_blocks_managed_by(request.user)
				response = render_to_response('qmul_import.html',{'form': form, 'subnets':subnets, 'type': 'DHCP'})
		else:
			form = UploadFileForm()
			subnets = get_address_blocks_managed_by(request.user)
			response = render_to_response('qmul_import.html',{'form': form, 'subnets':subnets, 'type': 'DHCP'})
	else:
		response =  render_to_response('qmul_import.html', {'PermissionError': True})
		
	return response
