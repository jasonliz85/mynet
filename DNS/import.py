from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from subnets.DNS.models import *
from subnets.DNS.forms import UploadFileForm
from subnets.AccessControl.views import get_address_blocks_managed_by, get_dns_patterns_managed_by
from django.contrib.auth.decorators import login_required
from netaddr import IPAddress
import re
def is_unique_custom(user, record_list, hard_check, soft_check):
	
	return record_list, errormsg
def is_permitted_custom(user, value_list):	
	errormessage = list()
	record_list = list()
	ip_blocks = get_address_blocks_managed_by(user)
	dns_expressions  = get_dns_patterns_managed_by(user)
	for value in value_list:
		has_permission = False
		if value['dns_type'] == '2NA':
			for item in dns_expressions: #for each dns expression in all dns expressions in the list...
				temp = '\S' + item.expression #...modify expression...
				if re.match(re.compile(temp), value['name']): #... and check if matches with input dns_name
					has_permission = True
					record_list.append(value)
					break
			if not has_permission:
				var = 'line %s, You are not allowed to add this DNS Name: %s, it is not part of your network resource group.\n' % (value['line_no'], value['name'])
				errormessage.append(var)
		elif value['dns_type'] == '3AN':
			for block in ip_blocks: #for each ip address block in all ip address blocks in the list...
				if value['ip_address'] in block.ip_network: #...check if ip_address is within range
					has_permission = True
					record_list.append(value)			
					break
			if not has_permission:
				var = 'line %s, You are not allowed to add this IP Address: %s, it is not part of your network resource group.\n' % (value['line_no'], value['ip_address'])
				errormessage.append(var)
		elif value['dns_type'] == '1BD':
			for block in ip_blocks: #for each ip address block in all ip address blocks in the list...
				if value['ip_address'] in block.ip_network: #...check if ip_address is within range
					has_permission = True			
					break
			if has_permission:
				has_permission = False
				for item in dns_expressions: #for each dns expression in all dns expressions in the list...
					temp = '\S' + item.expression #...modify expression...
					if re.match(re.compile(temp), value['name']): #... and check if matches with input dns_name
						has_permission = True
						record_list.append(value)
						break
				if not has_permission:
					var = 'line %s, You are not allowed to add this DNS Name: %s, it is not part of your network resource group.\n' % (value['line_no'], value['name'])
					errormessage.append(var)
			else:
				var = 'line %s, You are not allowed to add this IP Address: %s, it is not part of your network resource group.\n' % (value['line_no'], value['ip_address'])
				errormessage.append(var)
				
	return has_permission, errormessage
def FindValuesFromSplittedLine(splitted_line, l_no):
	'''
	To comment:
	'''
	#dns values to be populated, ttl is not neccessary and is optional
	values = {'dns_type': '', 'ip_address':'', 'name':'', 'ttl': 0, 'description':'', 'line_no': l_no}
	error = ''
	counter = 0
	
	for segment in splitted_line:
		if counter == 0:
			if segment == '+':
				values['dns_type'] = '2NA'
			elif segment == '=':
				values['dns_type'] = '1BD'
			elif segment == '^':
				values['dns_type'] = '3AN'
			else:
				error = 'Invalid DNS type %s, should be either ^, + or =' % segment
		if counter == 1:	
			if not segment:
				error = 'Record must have a machine name' 
			else:
				values['name'] = segment.rstrip('.')
		elif counter == 2:
			if not segment:
				error = 'Record must have an IP address' 
			else:
				try:
					values['ip_address'] = IPAddress(segment)
				except:
					error = 'Invalid IP address %s' % segment
		elif counter == 3:
			try:
				values['ttl'] = int(segment)
			except ValueError:
				values['ttl'] = 0
		elif counter == 4:
			values['description'] = segment
		counter = counter + 1
		
	return values, error

def handle_uploaded_file(request, f):
	'''
	Handles imported dns file to add to database
	'''
	Error = {'Type': '', 'is_error': False, 'Msg':''} 
	errormsg = list()
	record_list = list()
	records = list() 
	line_count = 0
	#First, check formating
	for line in f:
		line_count = line_count + 1
		if line[0] in ['=','^','+']:
			records.append(line)
			line = line.strip()
			splitted = line.split(':')
			if len(splitted) == 0:
				var = 'line %s, Invalid line formatting, \"%s\"\n' % (line_count, line)
				errormsg.append(var)
			else:
				values, error = FindValuesFromSplittedLine(splitted, line_count)
			if error:
				var = 'line %s, %s, \"%s\"\n' % (line_count, error, line)
				errormsg.append(var)
			else:
				record_list.append(values)
	if errormsg:
		Error['Type'] = 'Invalid file formatting'
		Error['Msg'] = errormsg
		Error['is_error'] = True
		return records, Error
	#Second, check if user is permitted
	record_list, errormsg = is_permitted_custom(request.user, record_list)
	if errormsg:
		Error['Type'] = 'Permission error, you are not allowed to import one or more records'
		Error['Msg'] = errormsg
		Error['is_error'] = True
		return records, Error
	#Third, do a unique check 
	record_list, errormsg = is_unique_custom(request.user, record_list, enable_hard_check = True, enable_soft_check = True)
	if errormsg:
		Error['Type'] = 'Unique error, one or more records import one or more records'
		Error['Msg'] = errormsg
		Error['is_error'] = True
		return records, Error
	#Add/Edit records to database
	for to_add in to_add_list:
		AddAndLogRecord()
	for to_modify in to_modify_list:
		EditAndLodRecord()

	return records, Error
@login_required
def import_dns(request):
	'''
	Import DNS functional page and form. Passes file (specified by the user) to handle_uploaded_file function and deals 
	approprietly with the response.
	'''
	if request.user.is_staff:
		if request.method == 'POST':
			form = UploadFileForm(request.POST, request.FILES)
			if form.is_valid():
				log, error = handle_uploaded_file(request, request.FILES['file'])
				#return HttpResponseRedirect('/dns/')
				pageContext = {'type': 'DNS', 'error': error['is_error'], 'errormessage':error['Msg'] , 'errortype':error['Type'], 'log': log}
				return render_to_response('qmul_import_result.html', pageContext)
		else:
			form = UploadFileForm()

		return render_to_response('qmul_import.html',{'form': form, 'type': 'DNS'})
	else:
		return render_to_response('qmul_import.html', {'PermissionError': True})
