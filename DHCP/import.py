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
	This function separates the elements in list that contains the values for each record (splitted_line) and converts 
	into a python dictionary for easier processing later in the import process. It also provides a low level validation 
	check for each value in the list. 
	'''
	#dns values to be populated, ttl is not neccessary and is optional
	values = {'record_type':''}
	error = ''
	counter = 0
	for segment in splitted_line:
		if counter == 0:
			values['line_no'] = l_no
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
def permission_check(subnet, record_list):
	'''
	Checks that the user is permitted to add/modify/delete each record in the pool and machines dictionaries. Will
	return an error if this check is not passed.
	'''
	Error = {'Type': '', 'is_error': False, 'Msg':''} 
	errormsg = list()
	for record in record_list:
		is_permitted = False
		if record['record_type'] == 'host':
			if record['ip_address'] < subnet[-1] and record['ip_address'] > subnet[0]:
				is_permitted = True
		elif record['record_type'] == 'pool':
			if record['ip_first'] < subnet[-1] and record['ip_first'] > subnet[0] and record['ip_last'] < subnet[-1] and record['ip_last'] > subnet[0]:
				is_permitted = True
		if not is_permitted:
			var = 'line %s, You do not have permission to change the IP address on this line.\n' % record['line_no']
			errormsg.append(var)
	if errormsg:
		Error['Type'] = 'Permission error, you are not allowed to import one or more records'
		Error['Msg'] = errormsg
		Error['is_error'] = True		
	return record_list, Error
def internal_unique_check(record_list):
	'''
	Checks that the right fields in all the records in the dictionaries are unique (as specified in the documentation).
	If this is condition is not met then this function will return an error.
	'''
	Error = {'Type': '', 'is_error': False, 'Msg':''} 
	errormsg = list()
	record_list_pool = list()
	record_list_host = list()
	for record in record_list:
		if record['record_type'] == 'host':
			record_list_host.append(record)
		elif record['record_type'] == 'pool':
			record_list_pool.append(record)
	if record_list_host:
		#check internal uniqueness
		for record in record_list_host:
			is_unique = True
			for record_check in record_list_host:
				if not record['line_no'] == record_check['line_no']:
					if record['ip_address'] == record_check['ip_address']:
						is_unique = False
						var = 'line %s, this IP address - %s - has been used more than once.\n' % (record['line_no'], record['ip_address'])
						errormsg.append(var)
						record_list_host.remove(record_check)
						break
					elif record['mac_address'] == record_check['mac_address']:
						var = 'line %s, this MAC address - %s - has been used more than once.\n' % (record['line_no'], record['mac_address'])
						errormsg.append(var)
						record_list_host.remove(record_check)
						break
					elif record['host_name'] == record_check['host_name']:
						var = 'line %s, this Host name - %s - has been used more than once.\n' % (record['line_no'], record['host_name'])
						errormsg.append(var)
						record_list_host.remove(record_check)
						break
	if record_list_pool:
		for record in record_list_pool:
			is_unique = True
			for record_check in record_list_pool:
				if not record['line_no'] == record_check['line_no']:
					if record['ip_first'] == record_check['ip_first']:
						is_unique = False
						var = 'line %s, this IP address - %s - has been used more than once.\n' % (record['line_no'], record['ip_first'])
						errormsg.append(var)
						record_list_pool.remove(record_check)
						break
					elif record['ip_last'] == record_check['ip_last']:
						var = 'line %s, this MAC address - %s - has been used more than once.\n' % (record['line_no'], record['ip_last'])
						errormsg.append(var)
						record_list_pool.remove(record_check)
						break
	if errormsg:
		Error['Type'] = 'Uniqueness error, one or more records are duplicated within this uploaded file.'
		Error['Msg'] = errormsg
		Error['is_error'] = True
	return record_list_pool, record_list_host, Error
	
def host_name_check(subnet, record_list_host):
	'''
	This function checks the uniqueness of the dhcp machine host name, which must be unique.
	Returns an error if a record is not unique.
	'''
	Error = {'Type': '', 'is_error': False, 'Msg':''} 
	errormsg = list()
	complex_host_name_queries = list()
	import operator
	if record_list_host:
		for record in record_list_host:
			complex_host_name_queries.append(Q(host_name = record['host_name']))
	
	complex_subnet_exclude = Q(ip_address__lt = subnet[-1])&Q(ip_address__gt = subnet[0])
	if complex_host_name_queries:
		found_like_host_names = DHCP_machine.objects.filter(reduce(operator.or_, complex_host_name_queries)).exclude(complex_subnet_exclude)
	if found_like_host_names:
		for each_record in found_like_host_names:
			for record in record_list_host:
				if record['host_name'] == each_record.host_name:
					var = 'line %s, this Host Name - %s - has already been used in the database (record id:%s).\n' %(record['line_no'], record['host_name'], each_record.id)
					errormsg.append(var)
	if errormsg:
		Error['Type'] = 'Uniqueness Error, one or more records in the database have the same host names.'
		Error['Msg'] = errormsg
		Error['is_error'] = True
	return record_list_host, Error
	
def overlapping_check(record_list_pool, record_list_host):
	'''
	Checks for overlapping between pools and hosts.
	To Do:
	'''
	Error = {'Type': '', 'is_error': False, 'Msg':''} 
	errormsg = list()
	#1.First check if pools are overlapping another pool or another fixed-address record_check
	#1a.ip pools
	for ip_pool_check in record_list_pool: 
		is_overlapped = False
		try:
			ip_range_check = IPRange(ip_pool_check['ip_first'], ip_pool_check['ip_last'])
		except AddrFormatError:
			errormsg.append('line %s, IP pool in error, lower bound IP greater than upper bound!\n'% ip_pool_check['line_no'])
			record_list_pool.remove(ip_pool_check)
			break
		for ip_pool in record_list_pool:
			if not ip_pool['line_no'] == ip_pool_check['line_no']:
				try:
					ip_range = IPRange(ip_pool['ip_first'], ip_pool['ip_last'])
				except AddrFormatError:
					errormsg.append('line %s, IP pool in error, lower bound IP greater than upper bound!\n'% ip_pool['line_no'])
					record_list_pool.remove(ip_pool)
					break
				if ip_range in ip_range_check:
					is_overlapped = True
					var = 'line %s, You cannot add this range, %s - %s. It is overlapping the existing range: %s - %s.\n' %(ip_pool['line_no'], ip_pool_check['ip_first'], ip_pool_check['ip_last'], ip_pool['ip_first'], ip_pool['ip_last'])
					errormsg.append(var)
					record_list_pool.remove(ip_pool)
					break
				elif ip_range_check in ip_range:
					is_overlapped = True
					var = 'line %s, You cannot add this range, %s - %s. It has been overlapped by the existing range: %s - %s.\n' %(ip_pool['line_no'],ip_pool['ip_first'], ip_pool['ip_last'], ip_pool_check['ip_first'], ip_pool_check['ip_last'])
					errormsg.append(var)
					record_list_pool.remove(ip_pool)
					break
				else:
					for ip in ip_range:
						if ip in ip_range_check:
							is_overlapped = True
							var = 'line %s, You cannot add this range, %s - %s, because one or more of it\'s IP address is overlapping the existing range: %s - %s.\n' %(ip_pool['line_no'], ip_pool_check['ip_first'], ip_pool_check['ip_last'], ip_pool['ip_first'], ip_pool['ip_last'])
							errormsg.append(var)
							record_list_pool.remove(ip_pool)
							break
	#1.b machine ip address
	if not is_overlapped and record_list_host:
		for ip_pool_check in record_list_pool: 
			is_overlapped = False
			try:
				ip_range_check = IPRange(ip_pool_check['ip_first'], ip_pool_check['ip_last'])
			except AddrFormatError:
				errormsg.append('line %s, IP pool in error, lower bound IP greater than upper bound!\n'% ip_pool_check['line_no'])
				record_list_pool.remove(ip_pool_check)
				break
			for record_host in record_list_host:
				print record_host['ip_address'], ip_range_check
				if record_host['ip_address'] < ip_range_check[-1] and record_host['ip_address'] > ip_range_check[0]:
					is_overlapped = True
					var = 'line %s, You cannot add this range, %s - %s, because it is overlapping fixed-address host registration (line no:%s).' %(ip_pool_check['line_no'], ip_pool_check['ip_first'], ip_pool_check['ip_last'], record['line_no'])
					errormsg.append(var)
					record_list_pool.remove(ip_pool_check)
					break
				
	#2.Now check if host names are overlapping with ip pools
	if record_list_host:
		for host_check in record_list_host:
			is_overlapped = False
			for ip_pool_check in record_list_pool:
				if host_check['ip_address'] > ip_pool_check['ip_first'] and host_check['ip_address'] < ip_pool_check['ip_last']:
					is_overlapped = True
					var = 'line %s, You cannot add this IP address, %s, because an exisiting IP range, %s - %s, is overlapping this address.' %(host_check['line_no'], host_check['ip_address'],ip_pool_check['ip_first'],ip_pool_check['ip_last'] )
					record_list_host.remove(host_check)
					break
			
	if errormsg:
		Error['Type'] = 'Overlapping error, one or more records are duplicated within this uploaded file.'
		Error['Msg'] = errormsg
		Error['is_error'] = True
		
	return record_list_pool, record_list_host, Error
	
def compare_import_and_live_records():
	'''
	To Do:
	'''
	to_add = list() 
	to_delete = list() 
	to_edit = list()
	Error = {'Type': '', 'is_error': False, 'Msg':''} 
	errormsg = list()
	if errormsg:
		Error['Type'] = 'Uniqueness error, one or more records are duplicated within this uploaded file.'
		Error['Msg'] = errormsg
		Error['is_error'] = True
	return to_add, to_delete, to_edit, Error
def handle_uploaded_file(request_obj, uploaded_file, subnet_list):
	'''
	Handles the import file and is in charge of making all the nessessary checks before making changes in the live database.
	#format check
		#for each_subnet in subnet_list:
			#try:
				#get_live_data for each_subnet
				#permission check
				#uploaded file internal unique check
				#host name uniqueness check
				#overlapping check
				#compare each_subnet with live_data_subset
				#retrieve and add to overall list to_add, to_edit, to_delete
			#except:
				#error along the other processes
			
	#if there are no errors:
		#delete_records
		#add_records
		#modify_records
	'''
	
	[records, error_msg] = format_check(uploaded_file)
	
	if error_msg['is_error']:
		return records, error_msg
	for each_subnet in subnet_list:
		[records, error_msg] = permission_check(each_subnet, records)
		if error_msg['is_error']:
			return records, error_msg
		[records_pool,records_host, error_msg] = internal_unique_check(records)
		if error_msg['is_error']:
			return records, error_msg
		if records_host:
			[records_host, error_msg] = host_name_check(each_subnet, records_host)
			if error_msg['is_error']:
				return records, error_msg
		[records_pool,records_host, error_msg] = overlapping_check(records_pool,records_host)
		if error_msg['is_error']:
			return records, error_msg
		[to_add, to_delete, to_edit, error_msg ] = compare_import_and_live_records()	
		if error_msg['is_error']:
			return records, error_msg
			
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
