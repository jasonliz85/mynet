from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext
from django.contrib.auth.decorators import login_required
from subnets.DNS.models import *
from subnets.AccessControl.views import get_address_blocks_managed_by
from netaddr import *

def get_and_format_subnet_data( user_obj, subnet):
	'''
	This function is responsible for getting the permitted dns records and formating it in the export format.
	See DNS.models.ExportRepresentation() for information about how the records are formatted
	'''
	formatted_data = ''
	if subnet == 'all':
		subnets = get_address_blocks_managed_by(user_obj)
		formatted_data = '# Subnets belonging to: %s #\n' %subnets
		records = DNS_name.objects.get_permitted_records(user_obj, True, 'ip', 'asc', '')
	else:
		formatted_data = '#################### Subnet:%s ####################\n' % (str(subnet))
		records = DNS_name.objects.get_records_in_subnet(user_obj, subnet)
	
	if records:
		for each_record in records:
			formatted_data = formatted_data + each_record.ExportRepresentation()
	else:
		formatted_data = formatted_data + '#None'

	return formatted_data
	
@login_required
def export_dns(request):
	'''
	This function is responsible for acquiring, formatting and exporting the appropriete and permitted dns records. 
	'''
	if request.user.is_staff:
		if request.method == 'POST':
			subnet = request.POST.get('subnets')
			if subnet == 'all':
				data = get_and_format_subnet_data(request.user, subnet)
				response = HttpResponse(data, mimetype='application/text')
				response['Content-Disposition'] = 'attachment; filename=dns_%s.txt' %subnet
			else:
				try:
					subnet = IPNetwork(subnet)
					data = get_and_format_subnet_data(request.user, subnet)
					response = HttpResponse(data, mimetype='application/text')
					response['Content-Disposition'] = 'attachment; filename=dns_%s.txt' %subnet
				except:
					subnets = get_address_blocks_managed_by(request.user)
					response = render_to_response('qmul_export.html',{'subnets':subnets,'type': 'DNS'},context_instance=RequestContext(request))
		else:
			subnets = get_address_blocks_managed_by(request.user)
			response = render_to_response('qmul_export.html',{'subnets':subnets,'type': 'DNS'},context_instance=RequestContext(request))
	else:
		response = render_to_response('qmul_import.html', {'PermissionError': True}, context_instance=RequestContext(request))
	
	return response

