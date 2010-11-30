from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from subnets.DNS.models import *
from subnets.DNS.forms import UploadFileForm
from subnets.AccessControl.views import get_address_blocks_managed_by, get_dns_patterns_managed_by
from django.contrib.auth.decorators import login_required
from netaddr import IPAddress
import re
def is_unique_custom(user_obj, value_list, soft_check):
	'''
	Checks the uniqueness of a record based on the ip address (ip, assummed netaddr IPAddress object), machine name (mname) and dns type (dt).
	Returns True if unique, False otherwise.
	By default, this function will perform a hard check based on a strict non-duplicated record (i.e. if ip, mname and dt are not already
	in the database). If enable_softcheck is True, this function will also perform the following:
	#3. Apply softer check, in three parts
	# a.if type is address to name, must check that the ip address is NOT mapped to another name (i.e. one address -> one name)
	# b.if type is name to address, must check that the name is NOT mapped to another ip address (i.e. one name -> one address)
	# c.if type is bi-directional, must check for both conditions a AND b
	'''
	#Algorithm
	#I.Initialise variables
	warningmessage = list()
	found_records = DNS_name.objects.get_permitted_records(user_obj, True, 'ip', 'asc', '')
	for value in value_list:
		has_permission = False
		already_exists = False
		dt = value['dns_type']
		ip = value['ip_address']
		mname = value['name']
		dscr = value['description']
		ttl = value['ttl']
		#2.Check if item exists in already permittable records. if yes, mark record as an edit, if no mark recors as an add
		for record in found_records:
			if record.ip_address == ip and record.name == mname and record.dns_type == dt and record.ttl == ttl and record.description == dscr:
				value['id'] = record.id
				value['action'] = 'skip'
				already_exists = True
				warningmessage.append('line %s, record already exists, therefore skipped.'% value['line_no'])
				break
			elif record.dns_type == dt:
				if dt == '3AN' and record.ip_address == ip: 	#address to name 	
					value['id'] = record.id
					value['action'] = 'edit'
					already_exists = True
					warningmessage.append('line %s, modified an existing address-name record (id:%s).'% (value['line_no'], record.id))
					break
				elif dt == '2NA' and record.name == mname: 	#name to address
					value['id'] = record.id
					value['action'] = 'edit'
					already_exists = True
					warningmessage.append('line %s, modified an existing name-address record (id:%s).'% (value['line_no'], record.id))
					break
				else: 			#else bi directional
					if record.ip_address == ip and record.name == mname:
						already_exists = True
					elif record.ip_address == ip:
						already_exists = True
					elif record.name == mname:
						already_exists = True	
					if already_exists:
						value['id'] = record.id
						value['action'] = 'edit'
						warningmessage.append('line %s, modified an existing bi-directional record (id:%s).'% (value['line_no'], record.id))
						break
			elif not already_exists:
				is_unique = do_uniqueness_check
				if unique:
					value['id'] = record.id
					value['action'] = 'add'
			
	return value_list, warningmessage, error
def is_permitted_custom(user, value_list):	
	errormessage = list()
	record_list = list()
	ip_blocks = get_address_blocks_managed_by(user)
	dns_expressions  = get_dns_patterns_managed_by(user)
	for value in value_list:
		has_permission = False
		if value['dns_type'] == '2NA':
			for item in dns_expressions: #for each dns expression in all dns expressions in the list...
				if re.match(re.compile(item.expression), value['name']): #... and check if matches with input dns_name
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
					if re.match(re.compile(item.expression), value['name']): #... and check if matches with input dns_name
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
		elif counter == 1:
			if not segment:
				error = 'Record must have an IP address' 
			else:
				try:
					values['ip_address'] = IPAddress(segment)
				except:
					error = 'Invalid IP address %s' % segment
		elif counter == 2:	
			if not segment:
				error = 'Record must have a machine name' 
			else:
				values['name'] = segment.rstrip('.')
		elif counter == 3:
			try:
				values['ttl'] = int(segment)
			except ValueError:
				values['ttl'] = 0
		elif counter == 4:
			values['description'] = segment
		counter = counter + 1
		
	return values, error

def handle_uploaded_file(request, import_file):
	'''
	Handles imported dns file to add to database
	'''
	Error = {'Type': '', 'is_error': False, 'Msg':''} 
	errormsg = list()
	record_list = list()
	records = list() 
	line_count = 0
	#First, check formating
	for line in import_file:
		line_count = line_count + 1
		if line[0] in ['=','^','+']:
			records.append(line)
			line = line.strip()
			splitted = line.split('\t')
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
	#Third, do a unique check and find values 
	record_list, warnmsg = is_unique_custom(record_list, enable_soft_check = True)
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
