from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
#-------import models
from subnets.DHCP.models import *
#-------import forms
from subnets.DHCP.forms import *
#-------import views
from subnets.helper_views import *
import datetime
import json
from netaddr import *

class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'
def suggest_a_host_name(host_name,ip_address,mac_address):
	#to Do
	return suggested_host_name
def prepare_values(action, table_type, vals, uname, m_id):
	'''
	Prepares the values, so as to be returned to the funtion AddAndLogRecord or EditAndLogRecord
	Arguments:
		action - 'A' Adding, or 'E' editing
		table_type - 'pool' or 'machine'
		vals - values to add to the database
		uname - django username objects
		m_id - if editing, specified the id of the record to be modified
	'''
	now = datetime.datetime.today()
	#initialising common values used for both 'E' and 
	if table_type == 'pool':
		values = {'ip_first':IPAddress(vals['IP_range1']), 'ip_last':IPAddress(vals['IP_range2']),'description':vals['dscr'] }
		table_number = '2'
		if values['ip_first'].version == 6 and values['ip_last'].version == 6:
			ipVersion = True
		else:
			ipVersion = False
	elif table_type == 'machine':
		values = {'mac_address' :str(EUI(vals['mcID'], dialect=mac_custom)),'ip_address': IPAddress(vals['ipID']),'host_name':vals['pcID'],'description':vals['dscr'] }
		table_number = '3'
		if values['ip_address'].version == 6:
			ipVersion = True
		else:
			ipVersion = False
	#perform individual actions
	if action == 'A':
		if table_type == 'pool':
			Record = DHCP_ip_pool( ip_first	= values['ip_first'],ip_last = values['ip_last'], is_ipv6 = ipVersion, 
				time_created = now, time_modified = now, description = values['description'])
		elif table_type == 'machine':
			Record = DHCP_machine( mac_address = values['mac_address'], ip_address = values['ip_address'], host_name = values['host_name'],
				is_ipv6 = ipVersion, time_created = now, time_modified = now, description = values['description'])
		preparedValues = Record, uname, table_number	
	elif action == 'E':
		is_modified = False
		if table_type == 'pool':
			try :
				ModifiedRecord = DHCP_ip_pool.objects.get(id = m_id)
			except model_name.DoesNotExist:
				return False
			valuesBefore = ModifiedRecord.LogRepresentation()
			if not ModifiedRecord.ip_first == values['ip_first']:
				ModifiedRecord.ip_first = values['ip_first']
				ModifiedRecord.is_ipv6 = ipVersion
				is_modified = True
			if not ModifiedRecord.ip_last == values['ip_last']:
				ModifiedRecord.ip_last = values['ip_last']
				is_modified = True
		elif table_type == 'machine':
			try :
				ModifiedRecord = DHCP_machine.objects.get(id = m_id)
			except model_name.DoesNotExist:
				return False
			valuesBefore = ModifiedRecord.LogRepresentation()
			if not ModifiedRecord.mac_address == values['mac_address']:
				ModifiedRecord.mac_address = values['mac_address']
				is_modified = True
			if not ModifiedRecord.ip_address == values['ip_address']:
				ModifiedRecord.ip_address = values['ip_address']
				ModifiedRecord.is_ipv6 = ipVersion
				is_modified = True
			if not ModifiedRecord.host_name == values['host_name']:
				ModifiedRecord.host_name = values['host_name']
				is_modified = True
		#common field between pools and machines: description
		if not ModifiedRecord.description == values['description']:
			if CompareDescriptions(ModifiedRecord.description, values['description']):
				ModifiedRecord.description = values['description']
				is_modified = True
		preparedValues = ModifiedRecord, uname, table_number, is_modified, valuesBefore, str(values)
		
	return preparedValues
#################################################################################
####################### DHCP IP Pool ############################################
#################################################################################
def ParameterChecks(user_object, ip1, ip2, mac, host, rid, is_ip_pools):
	"""
	This function calls is_unique and is_permitted dns test and consolidates errors. Returns True if there are no errors
	and return False otherwise. If there are errors, error_msg will contain a message relating to the nature of the error
	Arguments:
		user_object		= request object
		ip1			= ip address (in integer format) - if ip_pools, ip address start
		ip2			= if ip_pools, ip address finish
		mac			= mac address
		rid			= if present, the id of the record, usually an integer
		is_ip_pools		= if true, switches to DHCP_ip_pool model and handles appropriete values
	"""
	is_valid = False
	error_msg = ""
	if is_ip_pools:
		[is_valid, error_msg] = dhcp_permission_check(user_object, ip1, ip2, is_ip_pools)
		
	else:
		[is_valid, error_msg] = dhcp_permission_check(user_object, ip1, "", is_ip_pools)

	if not is_valid:
		return is_valid, error_msg
	else:
		if is_ip_pools:
			[is_valid, error_msg] = DHCP_ip_pool.objects.is_unique(user_object.user, ip1, ip2, rid)
			if is_valid:
				[is_overlapped, error_msg] = dhcp_is_ip_range_overlapping(ip1, ip2, user_object.user, rid)
				if is_overlapped:
					return False, error_msg
		else:
			[is_valid, error_msg] = DHCP_machine.objects.is_unique(user_object.user, ip1, mac, host, rid)
			if is_valid:
				[is_overlapped, error_msg] = dhcp_is_machine_name_overlapping_range(ip1, user_object.user)
				if is_overlapped:
					return False, error_msg
	return is_valid, error_msg
	
#Add a IP range to the DHCP IP pool model
@login_required
def dhcp_page_IP_range_add(request):
	'''
	'''
	if request.method == 'POST':
		form = Register_IP_range_Form(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			[can_pass, custom_errors] = ParameterChecks(request, IPAddress(info['IP_range1']), IPAddress(info['IP_range2']), '', '', '', True)
			if can_pass:
				registeredID = AddAndLogRecord(prepare_values('A', 'pool', info, request.user, ''))
				#redirect results
				url = "/dhcp/pool/%s/view"%registeredID
				response = HttpResponseRedirect(url)					
			else:
				response = render_to_response('qmul_dhcp_create_IP_range.html',{'form':form ,'c_errors': custom_errors}, context_instance=RequestContext(request))
		else:
			response = render_to_response('qmul_dhcp_create_IP_range.html',{'form':form }, context_instance=RequestContext(request))
	else:
		form = Register_IP_range_Form(initial = {})
		response = render_to_response('qmul_dhcp_create_IP_range.html',{'form':form }, context_instance=RequestContext(request))
	return response 
#List all IP range records in the DHCP IP pool model
@login_required
def dhcp_page_IP_range_listing(request):
	#get order direction, and order type
	order_dir = request.GET.get('ot', 'desc')
	order_by = request.GET.get('o', 'ip')
	toggle_order = request.GET.get('tog', 'no')
	#get page index
	try:
		page_index = int(request.GET.get('pi', '1'))
	except ValueError:
		page_index = 1
	#toggle sort type and specify sort order
	sort = {}
	sort['order'] = order_by
	if toggle_order == 'yes':
		change_dir = True
		sort['toggle'] = change_dir
	else:
		change_dir = False
		sort['toggle'] = False	
	if order_dir == 'desc':
		sort['type'] = 'asc'
		sort['type_bef'] = 'desc'
	else:
		sort['type'] = 'desc'
		sort['type_bef'] = 'asc'
			
	#get permitted records
	registered_IP_pools = DHCP_ip_pool.objects.get_permitted_records(request, order_by, order_dir, change_dir)
	#get number of records per page
	try:
		list_length = int(request.GET.get('len', '400'))
	except ValueError:
		list_length = 100
	if not list_length:
		list_length = len(registered_IP_pools) 
	#set up pagination
	paginator = Paginator(registered_IP_pools, list_length, 5)
	try:
		page = paginator.page(page_index)
	except (EmptyPage, InvalidPage), e:
		page = paginator.page(paginator.num_pages)
	#get post details
	if request.method == 'POST':
		actionForm = ViewMachinesActionForm(request.POST)	
		action = request.POST['status']
		if actionForm.is_valid():
			item_selected = request.POST.getlist('cbox_id')
			if item_selected:			
				if action == 'del':
					mDelete = list()	
					for item in item_selected:
						mDelete.append(DeleteAndLogRecord(item, DHCP_ip_pool, request.user, 'DHCP_ip_pool', ''))
					mlength = len(mDelete)
					response = render_to_response('qmul_dhcp_delete_IP_range.html',{'machines':mDelete, 'mlength' : mlength}, context_instance=RequestContext(request))
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						response = render_to_response('qmul_dhcp_listings_IP_range.html', {'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort }, context_instance=RequestContext(request))
					else:
						regmachine = DHCP_ip_pool.objects.get(idns_typed = item_selected[0])
						response = render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regmachine}, context_instance=RequestContext(request))
				else:
					actionForm = ViewMachinesActionForm(initial = {})
					response = render_to_response('qmul_dhcp_listings_IP_range.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort }, context_instance=RequestContext(request))	
			else:		
				actionForm = ViewMachinesActionForm(initial = {})
				response = render_to_response('qmul_dhcp_listings_IP_range.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort }, context_instance=RequestContext(request))	
	else:
		actionForm = ViewMachinesActionForm(initial = {})
		response = render_to_response('qmul_dhcp_listings_IP_range.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort }, context_instance=RequestContext(request))
	return response 
#Viw a single IP range record on the DHCP IP pool model
@login_required
def dhcp_page_IP_range_view(request, ip_id):
	#check m_id
	try:
		ip_id = int(ip_id)
	except ValueError:
		raise Http404()	
	#check if id in database
	try:
		regpools = DHCP_ip_pool.objects.get(id = ip_id)
	except DHCP_ip_pool.DoesNotExist:
		return HttpResponseRedirect("/dhcp/pool/list/default")
	#check if permitted
	[is_valid, error_msg] = dhcp_permission_check(request, regpools.ip_first, regpools.ip_last, False)
	if not is_valid:
		return HttpResponseRedirect("/error/permission/")
	return  render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regpools}, context_instance=RequestContext(request))
#Delete a single IP range on the DHCP IP pool model
@login_required
def dhcp_page_IP_range_delete(request, ip_id):
	#check ip_id is an integer
	try:
		ip_id = int(ip_id)
	except ValueError:
		raise Http404()	
	#check if id in database
	try:
		val = DHCP_ip_pool.objects.get(id = ip_id)
	except DHCP_ip_pool.DoesNotExist:
		return HttpResponseRedirect("/dhcp/pool/list/default")
	#check if permitted	
	[is_valid, error_msg] = dhcp_permission_check(request, val.ip_first, val.ip_last, False)
	if not is_valid:
		return HttpResponseRedirect("/error/permission/")
	#delete record
	mDelete = list()
	mDelete.append(DeleteAndLogRecord(ip_id, DHCP_ip_pool, request.user, 'DHCP_ip_pool', ''))
	if mDelete == False:
		return HttpResponseRedirect("/dhcp/pool/list/default")
	mlength = len(mDelete)
	return render_to_response('qmul_dhcp_delete_IP_range.html',{'machines':mDelete, 'mlength':mlength}, context_instance=RequestContext(request))
#Edit a single IP range to the DHCP IP pool model
@login_required
def dhcp_page_IP_range_edit(request, ip_id):
	try:
		ip_id = int(ip_id)
	except ValueError:
		raise Http404()	
	if request.method == 'POST':
		editform = Register_IP_range_Form(request.POST)
		if editform.is_valid():
			info = editform.cleaned_data
			[can_pass, custom_errors] = ParameterChecks(request, IPAddress(info['IP_range1']), IPAddress(info['IP_range2']), '', '', ip_id, True)
			if can_pass:
				modID = EditAndLogRecord(prepare_values('E', 'pool', info, request.user, ip_id))
				#redirect response
				url = "/dhcp/pool/%s/view" % modID
				response = HttpResponseRedirect(url)
			else:
				editform = Register_IP_range_Form(initial = { 'IP_range1' :info['IP_range1'],'IP_range2' :info['IP_range2'],'dscr':info['dscr'] })
				response = render_to_response('qmul_dhcp_edit_IP_range.html',{'form':editform ,'ip_id': ip_id,'c_errors': custom_errors}, context_instance=RequestContext(request))
		else:
			response = render_to_response('qmul_dhcp_edit_IP_range.html', {'form':editform, 'ip_id': ip_id}, context_instance=RequestContext(request))
	else:
		try:
			regmachine = DHCP_ip_pool.objects.get(id = ip_id)	
			editform = Register_IP_range_Form(initial = {'IP_range1':str(IPAddress(regmachine.ip_first)),'IP_range2':str(IPAddress(regmachine.ip_last)),'dscr':regmachine.description})	
			response = render_to_response('qmul_dhcp_edit_IP_range.html', {'form':editform, 'ip_id': ip_id}, context_instance=RequestContext(request))
		except DHCP_ip_pool.DoesNotExist:
			response = HttpResponseRedirect("/dhcp/pool/list/default")	
	return response
#################################################################################
####################### DHCP Machine Registration ###############################
#################################################################################
#
@login_required
def dhcp_page_listings(request):
	registeredmachines =  DHCP_machine.objects.all().order_by("ip_address")
	return render_to_response('qmul_dhcp_listings.html', {'machinelists' : registeredmachines, 'viewmachine' : 'qmul_dhcp_viewmachine.html' }, context_instance=RequestContext(request))	

#Edit DHCP machine registered records 
@login_required	
def dhcp_page_machine_edit(request, m_id):
	try:
		m_id = int(m_id)
	except ValueError:
		raise Http404()	
	if request.method == 'POST':
		editform = RegisterMachineForm(request.POST)
		if editform.is_valid():
			info = editform.cleaned_data
			[can_pass, custom_errors] = ParameterChecks(request, IPAddress(info['ipID']), '', str(EUI(info['mcID'], dialect=mac_custom)),info['pcID'], m_id, False)
			if can_pass:
				modID = EditAndLogRecord(prepare_values('E', 'machine', info, request.user, m_id))
				#redirect response
				url = "/dhcp/machine/%s/view" % modID
				response = HttpResponseRedirect(url)
			else:
				try:
					e_errors = custom_errors['message']
					editform = RegisterMachineForm(initial = { 'mcID':info['mcID'],'ipID' :info['ipID'],'pcID':custom_errors['suggested_name'],'dscr':info['dscr'] })
				except TypeError:
					e_errors = custom_errors
				response =  render_to_response('qmul_dhcp_editmachine.html',{'form':editform ,'m_id': m_id,'c_errors': e_errors}, context_instance=RequestContext(request))
		else:	
			response =  render_to_response('qmul_dhcp_editmachine.html', {'form':editform, 'm_id': m_id}, context_instance=RequestContext(request))	
	else:
		try:
			regmachine = DHCP_machine.objects.get(id = m_id)		
			editform = RegisterMachineForm(initial = {'mcID':regmachine.mac_address,'ipID':str(regmachine.ip_address), 'pcID':regmachine.host_name,'dscr':regmachine.description})		
			response =  render_to_response('qmul_dhcp_editmachine.html', {'form':editform, 'm_id': m_id}, context_instance=RequestContext(request))
		except DHCP_machine.DoesNotExist:
			response =  HttpResponseRedirect("/dhcp/machine/list/")	
	return response
#
@login_required
def dhcp_page_machine_listing(request):	
	#get order direction, and order type
	order_dir = request.GET.get('ot', 'desc')
	order_by = request.GET.get('o', 'ip')
	toggle_order = request.GET.get('tog', 'no')
	#get page index
	try:
		page_index = int(request.GET.get('pi', '1'))
	except ValueError:
		page_index = 1
	#toggle sort type and specify sort order
	sort = {}
	sort['order'] = order_by
	if toggle_order == 'yes':
		change_dir = True
		sort['toggle'] = change_dir
	else:
		change_dir = False
		sort['toggle'] = False	
	if order_dir == 'desc':
		sort['type'] = 'asc'
		sort['type_bef'] = 'desc'
	else:
		sort['type'] = 'desc'
		sort['type_bef'] = 'asc'
			
	#get permitted records
	registeredmachines =  DHCP_machine.objects.get_permitted_records(request, order_by, order_dir, change_dir)
	#get number of records per page
	try:
		list_length = int(request.GET.get('len', '400'))
	except ValueError:
		list_length = 100
	if not list_length:
		list_length = len(registeredmachines) 
	#set up pagination
	paginator = Paginator(registeredmachines, list_length, 5)
	try:
		page = paginator.page(page_index)
	except (EmptyPage, InvalidPage), e:
		page = paginator.page(paginator.num_pages)
	#get details from form and display
	if request.method == 'POST':
		actionForm = ViewMachinesActionForm(request.POST)		
		action = request.POST['status']
		if actionForm.is_valid():
			item_selected = request.POST.getlist('cbox_id')
			if item_selected:			
				if action == 'del':
					mDelete = list()
					for item in item_selected:
						mDelete.append(DeleteAndLogRecord(item, DHCP_machine, request.user, 'DHCP_machine', ''))
					mlength = len(mDelete)
					response = render_to_response('qmul_dhcp_deletemachine.html',{'machines':mDelete, 'mlength':mlength}, context_instance=RequestContext(request))
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						response = render_to_response('qmul_dhcp_listings.html', {'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort}, context_instance=RequestContext(request))
					else:
						regmachine = DHCP_machine.objects.get(id = item_selected[0])
						response = render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine}, context_instance=RequestContext(request))
				else:
					actionForm = ViewMachinesActionForm(initial = {})
					response = render_to_response('qmul_dhcp_listings.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort}, context_instance=RequestContext(request))	
			else:		
				actionForm = ViewMachinesActionForm(initial = {})
				response = render_to_response('qmul_dhcp_listings.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort}, context_instance=RequestContext(request))	
	else:
		actionForm = ViewMachinesActionForm(initial = {})
		response = render_to_response('qmul_dhcp_listings.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort}, context_instance=RequestContext(request))
	return response
#Delete a single record in the DHCP registration model
@login_required
def dhcp_page_machine_delete_single(request, m_id):
	#check m_id is an integer
	try:
		m_id = int(m_id)
	except ValueError:
		raise Http404()	
	#check if id in database
	try:
		val = DHCP_machine.objects.get(id = m_id)
	except DHCP_machine.DoesNotExist:
		return HttpResponseRedirect("/dhcp/machine/list/")
	#check if permitted	
	[is_valid, error_msg] = dhcp_permission_check(request, val.ip_address, "", False)
	if not is_valid:
		return HttpResponseRedirect("/error/permission/")
	#delete record
	mDelete = list()
	mDelete.append(DeleteAndLogRecord(m_id, DHCP_machine, request.user, 'DHCP_machine', ''))
	if mDelete == False:
		return HttpResponseRedirect("/dhcp/machine/list/")
	mlength = len(mDelete)
	return render_to_response('qmul_dhcp_deletemachine.html',{'machines':mDelete, 'mlength':mlength}, context_instance=RequestContext(request))

#View a single registered machine in the DHCP model
@login_required
def dhcp_page_machine_view(request, m_id):
	#check m_id
	try:
		m_id = int(m_id)
	except ValueError:
		raise Http404()	
	#check if id in database
	try:
		regmachine = DHCP_machine.objects.get(id = m_id)
	except DHCP_machine.DoesNotExist:
		return HttpResponseRedirect("/dhcp/machine/list/")
	#check if permitted
	[is_valid, error_msg] = dhcp_permission_check(request, regmachine.ip_address, "", False)
	if not is_valid:
		return HttpResponseRedirect("/error/permission/")
	return  render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine}, context_instance=RequestContext(request))

#Add a machine to the DHCP registration model
@login_required	
def dhcp_page_machine_add(request):
	if request.method == 'POST':
		form = RegisterMachineForm(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			[can_pass, custom_errors] = ParameterChecks(request, IPAddress(info['ipID']), "", str(EUI(info['mcID'], dialect=mac_custom)), info['pcID'], '', False)
			if can_pass:
				registeredID = AddAndLogRecord(prepare_values('A', 'machine', info, request.user, ''))
				#redirect results
				url = "/dhcp/machine/%s/view"%registeredID
				response = HttpResponseRedirect(url)
			else:
				try:
					e_errors = custom_errors['message']
					form = RegisterMachineForm(initial = { 'mcID':info['mcID'],'ipID' :info['ipID'],'pcID':custom_errors['suggested_name'],'dscr':info['dscr'] })
				except TypeError:
					e_errors = custom_errors
				response = render_to_response('qmul_dhcp_createmachine.html',{'form':form ,'c_errors': e_errors}, context_instance=RequestContext(request))
		else:
			response = render_to_response('qmul_dhcp_createmachine.html', {'form':form }, context_instance=RequestContext(request))
	else:
		form = RegisterMachineForm(initial = {})
		response = render_to_response('qmul_dhcp_createmachine.html', {'form':form }, context_instance=RequestContext(request))
	return response
def dhcp_fetch_pool_data(request):
	'''
	'''
	error = ''
	records = ''
	subnet = request.GET.get('subnet', '')
	data_format = request.GET.get('format', 'txt')
	if len(subnet) == 0:
		error = 'No input subnet defined.'
	else:
		try:
			sb = IPNetwork(subnet)
			records,error = DHCP_ip_pool.objects.get_records_in_subnet(sb)
			if sb.version == 4:
				is_ipv6_subnet = False
			else:
				is_ipv6_subnet = True
		except Exception, e:
			error = 'Input subnet is incorrectly formatted.'
	if error:
		response =render_to_response('qmul_dhcp_range_data.txt', { 'error':error, 'is_ipv6_subnet': is_ipv6_subnet}, mimetype = 'text/plain')
	elif data_format == 'txt':
		response =render_to_response('qmul_dhcp_range_data.txt', {'records':records, 'error':error, 'is_ipv6_subnet': is_ipv6_subnet}, mimetype = 'text/plain')
	elif data_format == 'json':
		data = []
		if not records:
			data = ['#None']
		else:
			for record in records:
				data.append({'ip_first': str(record.ip_first),	'ip_last':str(record.ip_last),
							'description':record.description})
		response = HttpResponse(json.dumps(data, indent=2), mimetype='application/json')
	else:
		error = 'Unknown format type - %s' %data_format
		response = render_to_response('qmul_dhcp_range_data.txt', {'error':error, 'is_ipv6_subnet': is_ipv6_subnet}, mimetype = 'text/plain')
	return response
def dhcp_fetch_host_data(request):
	'''
	'''
	error = ''
	records = ''
	subnet = request.GET.get('subnet', '')
	data_format = request.GET.get('format', 'txt')
	if len(subnet) == 0:
		error = 'No input subnet defined.'
	else:
		try:
			sb = IPNetwork(subnet)
			records, error = DHCP_machine.objects.get_records_in_subnet(sb)
			if sb.version == 4:
				is_ipv6_subnet = False
			else:
				is_ipv6_subnet = True
		except:
			error = 'Input subnet is incorrectly formatted.'
	if error:
		response = render_to_response('qmul_dhcp_host_data.txt', {'error':error, 'is_ipv6_subnet': is_ipv6_subnet}, mimetype = 'text/plain')
	elif data_format == 'txt':
		response = render_to_response('qmul_dhcp_host_data.txt', {'records':records, 'error':error, 'is_ipv6_subnet': is_ipv6_subnet}, mimetype = 'text/plain')
	elif data_format == 'json':
		data = []
		if not records:
			data = ['#None']
		else:
			for record in records:
				data.append({'host_name':record.host_name, 'ip_address':str(record.ip_address),
							'mac_address': record.mac_address, 'description':record.description})
		response = HttpResponse(json.dumps(data, indent=2), mimetype='application/json')
	else:
		error = 'Unknown format type - %s' %data_format
		response = render_to_response('qmul_dhcp_host_data.txt', {'error':error, 'is_ipv6_subnet': is_ipv6_subnet}, mimetype = 'text/plain')
	return response
