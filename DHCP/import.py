from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from subnets.DHCP.models import *
from subnets.DHCP.forms import UploadFileForm
from subnets.AccessControl.views import get_address_blocks_managed_by, get_dns_patterns_managed_by
from netaddr import *

class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'

def FindValuesFromSplittedLine(splitted_line, l_no):
	'''
	To comment:
	'''
	#dns values to be populated, ttl is not neccessary and is optional
	values = {'record_type':''}
	error = ''
	counter = 0
	for segment in splitted_line:
		if counter == 0:
			if segment == 'host':
				values['record_type'] = segment
			elif segment == 'pool':
				values['record_type'] = segment
		if values['record_type'] == 'host':
			if counter == 1:
				if not segment:
					error = 'Record must have an IP address' 
				else:
					try:
						values['ip_address'] = IPAddress(segment)
					except:
						error = 'Invalid IP address %s' % segment
			elif counter == 2:	
				if not segment:
					error = 'Record must have MAC address' 
				else:
					try:
						values['mac_address'] = str(EUI(segment, dialect=mac_custom))
					except:
						error = 'Invalid MAC address %s' % segment
			elif counter == 3:
				if not segment:
					error = 'Record must have Host name' 
				else:
					values['host_name'] = segment.replace(' ','')
			elif counter > 3:
				values['description'] = segment.lstrip('#')
		elif values['record_type'] == 'pool':
			if counter == 1:
				if not segment:
					error = 'Record must have beginning IP address' 
				else:
					try:
						values['ip_first'] = IPAddress(segment)
					except:
						error = 'Invalid IP address %s' % segment
			elif counter == 2:	
				if not segment:
					error = 'Record must ending IP address' 
				else:
					try:
						values['ip_last'] = IPAddress(segment)
					except:
						error = 'Invalid IP address %s' % segment
			elif counter > 2:
				values['description'] = segment.lstrip('#')
		counter = counter + 1
	return values, error
#==========================================================================================================
def format_check(imported_file):
	'''
	This function accepts a file and processes each line. Must be in the specified DHCP format (see documentation). 
	If a line is not in the right format, this function will return a list of errors. Otherwise it parses each line
	and returns two dictionaries, machines and pools.
	'''
	Error = {'Type': '', 'is_error': False, 'Msg':''} 
	errormsg = list()
	record_list = list()
	line_count = 0
	for line in imported_file:
		line_count = line_count + 1
		line = line.strip()
		splitted = line.split('\t')
		if line[0] == '#':
			continue #skip comments
		elif len(splitted) == 0:
			var = 'line %s, Invalid line formatting, \"%s\"\n' % (line_count, line)
			errormsg.append(var)
			continue
		elif not line[0:4] in ['pool','host']:
			var = 'line %s, Invalid DHCP type (should be either pool or \'host\'): \'%s\',  \"%s\,"\n' % (line_count,splitted[0], line)
			errormsg.append(var)
			continue
		[values, in_error] = FindValuesFromSplittedLine(splitted, line_count)
		if in_error:
			var = 'line %s, %s, \"%s\"\n' % (line_count, in_error, line)
			errormsg.append(var)
		else:
			record_list.append(values)
				
	if errormsg:
		Error['Type'] = 'Invalid file formatting'
		Error['Msg'] = errormsg
		Error['is_error'] = True
	
	return record_list, Error
def permission_check():
	'''
	Checks that the user is permitted to add/modify/delete each record in the pool and machines dictionaries. Will
	return an error if this check is not passed.
	'''
	return 
def internal_unique_check():
	'''
	Checks that the right fields in all the records in the dictionaries are unique (as specified in the documentation).
	If this is condition is not met then this function will return an error.
	'''
	return 
def other_check():
	'''
	Any other checks that need to be implemented before comparing with live data
	'''
	#To Do
	return 
def compare_import_and_live_records():
	'''
	
	'''
	return 
def handle_uploaded_file(request_obj, uploaded_file, subnet_list):
	'''
	Handles the import file and is in charge of making all the nessessary checks before making changes in the live database.
	'''
	#format check
	[records, error_msg] = format_check(uploaded_file)
	if error_msg['is_error']:
		return records, error_msg
	#for each_subnet in subnet_list:
		#try:
			#get_live_data for each_subnet
			#permission check
			#uploaded file internal unique check
			#other checks?
			#compare each_subnet with live_data_subset
			#retrieve and add to overall list to_add, to_edit, to_delete
		#except:
			#error along the other processes
	#if there are no errors:
		#delete_records
		#add_records
		#modify_records

	return records, error_msg

@login_required
def import_dhcp(request):
	'''
	Import dhcp functional page and form. Passes file (specified by the user) to handle_uploaded_file function and deals 
	approprietly with the response.
	'''
	if request.user.is_staff:
		if request.method == 'POST':
			form = UploadFileForm(request.POST, request.FILES)
			subnet = request.POST.get('subnets')
			if form.is_valid():
				if subnet == 'all':
					subnet = get_address_blocks_managed_by(request.user)
					log, error = handle_uploaded_file(request, request.FILES['file'], subnet)
					pageContext = {'type': 'DHCP', 'error': error['is_error'],
									'errormessage':error['Msg'] , 'errortype':error['Type'], 
									'log': log}
					response = render_to_response('qmul_import.html',{'form': form, 'subnets':subnet, 'type': 'DHCP'})
				else:
					#try:	
						subnet = [IPNetwork(subnet)]
						log, error = handle_uploaded_file(request, request.FILES['file'], subnet)
						pageContext = {'type': 'DHCP', 'error': error['is_error'],
										'errormessage':error['Msg'] , 'errortype':error['Type'], 
										'log': log}
						response = render_to_response('qmul_import_result.html', pageContext)
					#except Exception, e:
					#	subnets = get_address_blocks_managed_by(request.user)
					#	print e
					#	response = render_to_response('qmul_import.html',{'form': form, 'subnets':subnets, 'type': 'DHCP'})
			else:
				subnets = get_address_blocks_managed_by(request.user)
				response = render_to_response('qmul_import.html',{'form': form, 'subnets':subnets, 'type': 'DHCP'})
		else:
			form = UploadFileForm()
			subnets = get_address_blocks_managed_by(request.user)
			response = render_to_response('qmul_import.html',{'form': form, 'subnets':subnets, 'type': 'DHCP'})
	else:
		response =  render_to_response('qmul_import.html', {'PermissionError': True})
		
	return response
