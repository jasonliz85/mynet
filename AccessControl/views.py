from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict
from mynet.AccessControl.models import *
from mynet.AccessControl.forms import *
from mynet.HistoryLog.models import *
from mynet.HistoryLog.views import *
from mynet.views import *

from django.db.models import Q, F

from netaddr import *
from django.utils.html import escape 

import django.forms as forms 
import datetime, json, difflib

class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'
def LogEvent(action,val_bef, val_aft, is_bulk, uname, gname, tname, tid):
	"""
	This function logs an event  a Record in the database and logs the event in the HistoryLog db. It returns 
	a list of the fields and values that were deleted.
		values: m_id = unique id of record in db, model_name = name of the table in db
	"""
	
	currentNetGroup = Group.objects.get(name = "Network Group")		#netgroup.objects.get(name = ngroup)
	currentUser     = User.objects.get(username__exact = uname)	#usrname.objects.get(uname = user)
	now = datetime.datetime.today()
	newEvent = log( #NetGroupName 		= currentNetGroup,
			NetUser		 	= currentUser,
			TableName		= tname,
			RecordID		= tid,
			TimeOccured		= now,
			ActionType		= action,	
			ValuesBefore		= val_bef,
			ValuesAfter		= val_aft,
			IsBulk 			= is_bulk
		)	
	newEvent.save()
	return 
def CompareDescriptions(dsrc1, dsrc2):
	changed = bool(0)
	s = difflib.SequenceMatcher(None, dsrc1, dsrc2)
	for tag, i1, i2, j1, j2 in s.get_opcodes():
 		if tag == 'insert':
 			if dsrc1[i1:i2] == '' and dsrc2[j1:j2] == ' ' or dsrc1[i1:i2] == ' ' and dsrc2[j1:j2] == '':
 				changed = bool(0)
 			else:
 				changed = bool(1)
 		elif tag == 'replace':
 			if dsrc1[i1:i2] == '' and dsrc2[j1:j2] == ' ' or dsrc1[i1:i2] == ' ' and dsrc2[j1:j2] == '':
 				changed = bool(0)
 			else:
 				changed = bool(1)
 		elif tag == 'delete':
 			if dsrc1[i1:i2] == '' and dsrc2[j1:j2] == ' ' or dsrc1[i1:i2] == ' ' and dsrc2[j1:j2] == '':
 				changed = bool(0)
 			else:
 				changed = bool(1)
	return changed

def EditAndLogRecord(m_name_str, m_id, model_name, uname, values): 
	"""
	This function edits a Record in the database and logs the event in the HistoryLog db
		arguments: m_id = unique id of record in db, model_name = name of the table in db
	"""
	#initialize values
	is_modified = bool(0)
	mod_record = model_name.objects.get(id = m_id)
	valBef = mod_record.LogRepresentation()
	t_number = get_table_number(m_name_str)
	#switch to appropriete model and deal with each slightly differently
	if m_name_str == "DNS_names":	
		if not mod_record.name == values['name']: 
			mod_record.name = values['name']
			is_modified = bool(1)
		if not mod_record.description == values['description']:
			if CompareDescriptions(mod_record.description, values['description']):
				mod_record.description = values['description']
				is_modified = bool(1)	
		if not mod_record.dns_type == values['dns_type']:
			tp = values['dns_type']
			if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
				tp = '1BD'
			mod_record.dns_type = values['dns_type']
			is_modified = bool(1)
		if not mod_record.ip_address == int(IPAddress(values['ip_address'])):
			mod_record.ip_address = int(IPAddress(values['ip_address']))
			is_modified = bool(1)
			if (IPAddress(values['ip_address']).version == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			mod_record.is_ipv6 = ipVersion		
	elif m_name_str == "DHCP_ip_pool":
		if not mod_record.ip_first == int(IPAddress(values['ip_first'])):
			if (IPAddress(values['ip_first']).version == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			is_modified = bool(1)
			mod_record.ip_first = int(IPAddress(values['ip_first']))
			mod_record.is_ipv6 = ipVersion
		if not mod_record.ip_last == int(IPAddress(values['ip_last'])):
			mod_record.ip_last = int(IPAddress(values['ip_last']))
			is_modified = bool(1)
		if not mod_record.description == values['description']:
			if CompareDescriptions(mod_record.description, values['description']):
				mod_record.description = values['description']
				is_modified = bool(1)
	elif m_name_str == "DHCP_machine":
		if not mod_record.mac_address == str(EUI(values['mac_address'], dialect=mac_custom)):
			mod_record.mac_address = str(EUI(values['mac_address'], dialect=mac_custom))
			is_modified = bool(1)
		if not mod_record.ip_address == int(IPAddress(values['ip_address'])):
			mod_record.ip_address = int(IPAddress(values['ip_address']))
			if (IPAddress(values['ip_address']).version == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			mod_record.is_ipv6 = ipVersion
			is_modified = bool(1)
		if not mod_record.host_name == values['host_name']:
			mod_record.host_name = values['host_name']
			is_modified = bool(1)
		if not mod_record.description == values['description']:
			if CompareDescriptions(mod_record.description, values['description']):
				mod_record.description = values['description']
				is_modified = bool(1)
	else: 
		return bool(0)
		
	if is_modified:		
		now = datetime.datetime.today()
		final_values = str(values)
		init_values = str(valBef)
		mod_record.time_modified = now
		mod_record.save()
		LogEvent('E',init_values, final_values, False, uname, "NetGroup:ToDo", t_number, m_id)
		
	return mod_record.id

	
def AddAndLogRecord(m_name_str, model_name, uname, values):
	"""
	This function adds a Record in the database and logs the event in the HistoryLog db.
	"""
	now = datetime.datetime.today()
	t_number = get_table_number(m_name_str)
	#check ip address if version 6
	try: 
		if (IPAddress(values['ip_address']).version == 6):
			ipVersion = True
		else:
			ipVersion = False
	except KeyError:
		pass
	
	if m_name_str == "DNS_names":
		tp = values['dns_typ']
		if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
			tp = '1BD'
		newRecord = model_name( name	= values['name'],
					ip_address	= int(IPAddress(values['ip_address'])),
					dns_type	= tp,
					is_ipv6 	= ipVersion,
					time_created 	= now,
					time_modified	= now,
					description 	= values['description']								
					)
	elif m_name_str == "DHCP_ip_pool":		
		if (IPAddress(values['ip_first']).version == 6):
			ipVersion = bool(1)
		else:
			ipVersion = bool(0)				
		newRecord = model_name(	ip_first	= int(IPAddress(values['ip_first'])),
					ip_last		= int(IPAddress(values['ip_last'])),
					is_ipv6 	= ipVersion,
					time_created 	= now,					
					time_modified	= now,
					description 	= values['description']								
					)
	elif m_name_str == "DHCP_machine":
		newRecord = model_name(	mac_address 	= str(EUI(values['mac_address'], dialect=mac_custom)),
					ip_address  	= int(IPAddress(values['ip_address'])),
					host_name  	= values['host_name'],
					is_ipv6  	= ipVersion,
					time_created 	= now,
					time_modified	= now,
					description 	= values['description']
					)
	else: 
		return bool(0)
	newRecord.save() #vals = model_name.objects.filter(id = newRecord.id).values() 
	init_values = "{}" 
	final_values = newRecord.LogRepresentation()#str(vals[0])
	print final_values
	LogEvent('A',init_values, final_values, False, uname, "NetGroup:ToDo", t_number, newRecord.id)
	return newRecord.id
		
def DeleteAndLogRecord(m_id, Model_Name, uname, table_name, action):
	"""
	This function deletes a Record in the database and logs the event in the HistoryLog db. It returns 
	a list of the fields and values that were deleted.
		values: m_id = unique id of record in db, model_name = name of the table in db, uname =
	"""
	t_number = get_table_number(table_name)
	DeleteRecord = Model_Name.objects.get(id = m_id)
	init_values = DeleteRecord.LogRepresentation() 	#init_values = str(vals[0]) 	#json.dumps(vals[0], sort_keys=True, indent=0) 	
	final_values = "{}"				#json.dumps("{}", sort_keys=True, indent=0)   returnRecordList.append(DeleteRecord)
	DeleteRecord.delete()
	if len(action) == 0:
		action = 'D'
	#log event 
	LogEvent(action,init_values, final_values, False, uname, "NetGroup:ToDo", t_number, m_id)

	return DeleteRecord

#################################################################################
####################### DNS NAME Pair ###########################################
#################################################################################
#DNS_name pair
def dns_permission_check(request, ip_address, name, dns_typ):
	"""
	This function checks the name, ipaddress and dns type to see the record is allowed to be created. There are three check, stated below:
		bi-directional - two checks on each record is needed | permission for both ip address and machine name
		address to name - check only permission for ip address
		name to address - check only permisiion for machine name
	"""
	has_permission = False	
	custom_errors = list()
	message1 = 'You are not allowed to add this IP Address, it is not part of your network resource group.'
	message2 = 'You are not allowed to add this Machine Name, it is not part of your network resource group.'
	check1 = is_ipaddress_in_netresource(request, ip_address)
	check2 = is_name_in_netresource(request, name)
	if dns_typ == '1BD':
		if check1 == True and check2  == True:
			has_permission = True
		if not check1:
			custom_errors.append({'error':True, 'message': message1})
		if not check2:
			custom_errors.append({'error':True, 'message': message2})
	elif dns_typ == '2NA':
		if check2 == True:
			has_permission = True
		if not check2:
			custom_errors.append({'error':True, 'message': message2})
	else:
		if check1 == True:
			has_permission = True
		if not check1:
			custom_errors.append({'error':True, 'message': message1})	
	
	return has_permission, custom_errors

def get_permited_records(request, enable_type_filter):
	"""
	This function return a queryset from the model table DNS_names. The returned results are filtered by permitted
	ip_blocks, dns_expressions and dns_type that the user is able to access. If enable_type_filter is enabled, 
	a further filtering step is applied - please see comments this function for further information.
	"""
	#Get network groups, ip blocks and dns expressions which the user has permission to control
	[net_groups, ip_blocks, dns_exprs] = get_permissions_to_session(request)
	
	#first find all the ip addresses that the user has permission to control
	empty_find = True
	for block in range(len(ip_blocks)):
		ip_block = IPNetwork(str(ip_blocks[block]))
		ip_filter_upper = Q(ip_address__lt = ip_block[-1])
		ip_filter_lower = Q(ip_address__gt = ip_block[0])
		#filter the ip block
		finds = DNS_names.objects.filter( ip_filter_upper, ip_filter_lower )
		if block == 0:
			total_ip_finds = finds
			if len(finds) == 0:
				empty_find = True
			else:
				empty_find = False
		else:
			if len(finds) == 0:
				if empty_find:
					empty_find = True	
			else:
				if empty_find:
					total_ip_finds = finds
					empty_find = False
				else:
					total_ip_finds = finds|total_ip_finds
	#second, find all the dns names that the user can control
	empty_find = True
	for expression in range(len(dns_exprs)):
		dns_filter = Q(name__regex = ('\S' + str(dns_exprs[expression])))
		finds = DNS_names.objects.filter( dns_filter )
		if expression == 0:	
			total_name_finds = finds
			if len(finds) == 0:
				empty_find = True
			else:
				empty_find = False
		else:	
			if len(finds) == 0:
				if empty_find:
					empty_find = True	
			else:
				if empty_find:
					total_name_finds = finds
					empty_find = False
				else:
					total_name_finds = finds|total_name_finds
					
	if len(dns_exprs) > 0 and len(ip_blocks) > 0:
		combined_records = total_name_finds|total_ip_finds
	else:
		combined_records = list()
	#we now have a combimed result- great! we now need to filter these a bit more (assuming enable_filter_type is True)
	#so, if the type of record is:
	#bi-directional - two checks on each record is needed | permission for both ip address and machine name
	#address to name - check only permission for ip address
	#name to address - check only permisiion for machine name
	if enable_type_filter:
		type_filtered_records = list()
		for record in range(len(combined_records)):
			has_permission = False
			#dt = combined_records[record].dns_type		#dns type
			[has_permission, msg] = dns_permission_check(	request,
									combined_records[record].ip_address,
									combined_records[record].name,
									combined_records[record].dns_type)
			#checked for one of three types and checked whether the above conditions are true
			#if true, add to overall list to return
			if has_permission:
				type_filtered_records.append(combined_records[record])
		
		permitted_records = type_filtered_records
	else:
		permitted_records = combined_records
	
	return permitted_records

@login_required
def dns_namepair_simpleAdd(request, pair_id):
	try:
		pair_id = int(pair_id)
	except ValueError:
		raise Http404()	
	return handlePopAdd(request, Register_service_Form, 'services', pair_id)
	
#handle pop_up
def handlePopAdd(request, addForm, field, original_id):
	original_machine = DNS_names.objects.get(id = original_id)
	ip_address = original_machine.ip_address
	mn_pair = original_machine.name
	if request.method == "POST":
		form = addForm(request.POST)
		if form.is_valid():
			try:
				newObject = form.cleaned_data #form.save()
			except forms.ValidationError, error:
				newObject = None
			if newObject:
				[canpass, custom_errors] = dns_permission_check(request, int(IPAddress(original_machine.ip_address)), newObject['service_name'], "2NA")
				if canpass:
					values = { 	'name' :newObject['service_name'],'dns_typ' :"2NA",
							'ip_address' :original_machine.ip_address,'description':newObject['dscr'] }
					AddAndLogRecord('DNS_names', DNS_names, request.user.username, values)					
					display = "Added " + " " + newObject['service_name']
					return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script> <p>Test to display.</p>' %\
						(newObject, display )) #._get_pk_val()
				else:
					pageContext = {'form': form, 'field': field, 'mach':mn_pair, 'ip':str(IPAddress(ip_address)),'c_errors': custom_errors}
					return render_to_response("qmul_dns_create_simple.html", pageContext)
	else:		
		form = addForm(initial = {})
	
	pageContext = {'form': form, 'field': field, 'mach':mn_pair, 'ip':str(IPAddress(ip_address)) }
	return render_to_response("qmul_dns_create_simple.html", pageContext)

#Add an IP-name pair to modelquery set
@login_required
def dns_namepair_add(request):
	if request.method == 'POST':
		form = Register_namepair_Form(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			[can_pass, custom_errors] = dns_permission_check(request, int(IPAddress(info['ip_address'])),info['dns_expr'], info['dns_typ'])
			#check if this form is permitted first
			if can_pass:
				values = { 	'name' :info['dns_expr'],'dns_typ' :info['dns_typ'],
						'ip_address' :int(IPAddress(info['ip_address'])),'description':info['dscr'] }
				registeredID = AddAndLogRecord('DNS_names', DNS_names, request.user.username, values)
				namepair_registered  = DNS_names.objects.get(id = registeredID)
				namepair_registered.ip = str(IPAddress(namepair_registered.ip_address))
				add_service = request.POST.getlist('service_add')
				#if add_service parameter is triggered, will add the item to the model db
				if add_service:		
					for item in add_service:
						service_add = eval(item)
						values = { 	'name':service_add['dns_expr'],'dns_typ':service_add['dns_typ'],
								'ip_address':int(IPAddress(service_add['ip_address'])),'description':service_add['dscr'] }
						AddAndLogRecord('DNS_names', DNS_names, request.user.username, values)			
				#find all other associated services and display them
				tempFilter = DNS_names.objects.filter(ip_address = int(IPAddress(info['ip_address']))).exclude(id = registeredID)
				regServices = list()
				for i in range(len(tempFilter)):
					[is_service_permitted, msg] = dns_permission_check(request,int(IPAddress(tempFilter[i].ip_address)), tempFilter[i].machine_name, tempFilter[i].dns_type)
					if is_service_permitted:
						tempFilter[i].ip = str(IPAddress(tempFilter[i].ip_address))
						regServices.append(tempFilter[i])
				#render results
				return render_to_response('qmul_dns_view_namepair.html', {'machine': namepair_registered, 'machinelists':regServices})
			else:
				form = Register_namepair_Form(initial = {'dns_expr':info['dns_expr'],'dns_typ':info['dns_typ'],'ip_address':info['ip_address'],'dscr':info['dscr']})
				return render_to_response('qmul_dns_create_namepair.html',{'form':form ,'c_errors': custom_errors })
	else:
		form = Register_namepair_Form(initial = {})
	return render_to_response('qmul_dns_create_namepair.html',{'form':form })

#list all ip-name records in the model
@login_required
def dns_namepair_listing(request):
	
	registered_pairs =  get_permited_records(request, True)# DNS_names.objects.all()#.order_by("dns_type")
	#for display purposes, convert ip from integer form to str form (i.e. 3232235521 -> '192.168.0.1')
	for i in range(len(registered_pairs)):
		registered_pairs[i].ip = str(IPAddress(registered_pairs[i].ip_address))
		
	if request.method == 'POST':
		actionForm = ViewMachinesActionForm(request.POST)	
		action = request.POST['status']
		if actionForm.is_valid():
			item_selected = request.POST.getlist('cbox_id')
			if item_selected:			
				if action == 'del':
					mDelete = list()
					c_user = request.user.username
					for item in item_selected:
						mDelete.append(DeleteAndLogRecord(item, DNS_names, c_user, 'DNS_names', ''))
					mlength = len(mDelete)
					return render_to_response('qmul_dns_delete_namepair.html',{'machines':mDelete, 'mlength' : mlength})
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						return render_to_response('qmul_dns_listings_namepair.html', {'form':actionForm, 'machinelists' : registered_pairs })
					else:
						regmachine = DNS_names.objects.get(id = item_selected[0])
						regServices = DNS_names.objects.filter(ip_address = regmachine.ip_address).exclude(id = regmachine.id)
						return render_to_response('qmul_dns_view_namepair.html', {'machine': regmachine, 'machinelists':regServices})
				else:
					actionForm = ViewMachinesActionForm(initial = {})
					return render_to_response('qmul_dns_listings_namepair.html',{'form':actionForm, 'machinelists' : registered_pairs })	
			else:		
				actionForm = ViewMachinesActionForm(initial = {})
				return render_to_response('qmul_dns_listings_namepair.html',{'form':actionForm, 'machinelists' : registered_pairs })	
	else:
		actionForm = ViewMachinesActionForm(initial = {})
		return render_to_response('qmul_dns_listings_namepair.html',{'form':actionForm, 'machinelists' : registered_pairs})
	return render_to_response('qmul_dns_listings_namepair.html',{})

#view a single ip-name pair 
@login_required
def dns_namepair_view(request, pair_id):
	try:
		pair_id = int(pair_id)
	except ValueError:
		raise Http404()	
	regpair = DNS_names.objects.get(id = pair_id)
	regpair.ip = str(IPAddress(regpair.ip_address))
	#regServices = DNS_names.objects.filter(ip_pair = regpair.ip_pair).exclude(id = regpair.id)
	#for i in range(len(regServices)):
	#	regServices[i].ip = str(IPAddress(regServices[i].ip_pair))
		
	tempFilter = DNS_names.objects.filter(ip_address = regpair.ip_address).exclude(id = regpair.id)
	regServices = list()
	for i in range(len(tempFilter)):
		[is_service_permitted, msg] = dns_permission_check(request,int(IPAddress(tempFilter[i].ip_address)), tempFilter[i].name, tempFilter[i].dns_type)
		if is_service_permitted:
			tempFilter[i].ip = str(IPAddress(tempFilter[i].ip_address))
			regServices.append(tempFilter[i])
	return  render_to_response('qmul_dns_view_namepair.html', {'machine': regpair, 'machinelists': regServices})

#delete a single record 
@login_required
def dns_namepair_delete(request, pair_id):
	try:
		pair_id = int(pair_id)
	except ValueError:
		raise Http404()		
	mDelete = list()
	mDelete.append(DeleteAndLogRecord(pair_id, DNS_names, request.user.username, 'DNS_names', ''))
	mlength = len(mDelete)
	return render_to_response('qmul_dns_delete_namepair.html',{'machines':mDelete, 'mlength':mlength})
	
#edit a single record
@login_required
def dns_namepair_edit(request, pair_id):
	try:
		pair_id = int(pair_id)
	except ValueError:
		raise Http404()	
	if request.method == 'POST':
		editform = Register_namepair_Form(request.POST)
		if editform.is_valid():
			info = editform.cleaned_data
			[can_pass, custom_errors] = dns_permission_check(request, int(IPAddress(info['ip_address'])),info['dns_expr'], info['dns_typ'])
			if can_pass:
				valAft = { 	'name' :info['dns_expr'],'dns_type':info['dns_typ'],
						'ip_address' :info['ip_address'],'description' :info['dscr']	}
				modID = EditAndLogRecord('DNS_names', pair_id,  DNS_names,request.user.username, valAft)
				regpair = DNS_names.objects.get(id = modID)
				regpair.ip = str(IPAddress(regpair.ip_address))
				regServices = DNS_names.objects.filter(ip_address = regpair.ip_address).exclude(id = modID)
				for i in range(len(regServices)):
					regServices[i].ip = str(IPAddress(regServices[i].ip_address))
		
				return render_to_response('qmul_dns_view_namepair.html', {'machine': regpair, 'machinelists':regServices})
			else:
				form = Register_namepair_Form(initial = {'dns_expr':info['dns_expr'],'dns_typ':info['dns_typ'],'ip_address':info['ip_address'],'dscr':info['dscr']})
				return render_to_response('qmul_dns_create_namepair.html',{'form':form ,'c_errors': custom_errors })
	else:
		regpair = DNS_names.objects.get(id = pair_id)		
		editform = Register_namepair_Form(initial = {'dns_expr':regpair.name,'ip_address':str(IPAddress(regpair.ip_address)),'dscr':regpair.description, 'dns_typ': regpair.dns_type})	
	return render_to_response('qmul_dns_edit_namepair.html', {'form':editform, 'ip_id': pair_id})

#################################################################################
####################### DHCP IP Pool ############################################
#################################################################################

#Add a IP range to the DHCP IP pool model
@login_required
def dhcp_page_IP_range_add(request):
	if request.method == 'POST':
		form = Register_IP_range_Form(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			values = { 	'ip_first' :info['IP_range1'],'ip_last' :info['IP_range2'],
					'description':info['dscr'] }
			registeredID = AddAndLogRecord('DHCP_ip_pool',  DHCP_ip_pool, request.user.username, values)
			IP_pool_registered  = DHCP_ip_pool.objects.get(id = registeredID)
			#for display purposes
			IP_pool_registered.ip1 = str(IPAddress(IP_pool_registered.ip_first))
			IP_pool_registered.ip2 = str(IPAddress(IP_pool_registered.ip_last))					
			return render_to_response('qmul_dhcp_view_IP_range.html', {'machine': IP_pool_registered})
	else:
		form = Register_IP_range_Form(initial = {})

	return render_to_response('qmul_dhcp_create_IP_range.html',{'form':form })
#List all IP range records in the DHCP IP pool model
@login_required
def dhcp_page_IP_range_listing(request):
	registered_IP_pools =  DHCP_ip_pool.objects.all().order_by("ip_first")
	#for display purposes
	for i in range(len(registered_IP_pools)):
		registered_IP_pools[i].ip1 = str(IPAddress(registered_IP_pools[i].ip_first))
		registered_IP_pools[i].ip2 = str(IPAddress(registered_IP_pools[i].ip_last))
	if request.method == 'POST':
		actionForm = ViewMachinesActionForm(request.POST)	
		action = request.POST['status']
		if actionForm.is_valid():
			item_selected = request.POST.getlist('cbox_id')
			if item_selected:			
				if action == 'del':
					mDelete = list()	
					c_user = request.user.username
					for item in item_selected:
						mDelete.append(DeleteAndLogRecord(item, DHCP_ip_pool, c_user, 'DHCP_ip_pool', ''))
					mlength = len(mDelete)
					return render_to_response('qmul_dhcp_delete_IP_range.html',{'machines':mDelete, 'mlength' : mlength})
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						return render_to_response('qmul_dhcp_listings_IP_range.html', {'form':actionForm, 'machinelists' : registered_IP_pools })
					else:
						regmachine = DHCP_ip_pool.objects.get(idns_typed = item_selected[0])
						return render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regmachine})
				else:
					actionForm = ViewMachinesActionForm(initial = {})
					return render_to_response('qmul_dhcp_listings_IP_range.html',{'form':actionForm, 'machinelists' : registered_IP_pools })	
			else:		
				actionForm = ViewMachinesActionForm(initial = {})
				return render_to_response('qmul_dhcp_listings_IP_range.html',{'form':actionForm, 'machinelists' : registered_IP_pools })	
	else:
		actionForm = ViewMachinesActionForm(initial = {})
		return render_to_response('qmul_dhcp_listings_IP_range.html',{'form':actionForm, 'machinelists' : registered_IP_pools})
	
#Viw a single IP range record on the DHCP IP pool model
@login_required
def dhcp_page_IP_range_view(request, ip_id):
	try:
		ip_id = int(ip_id)
	except ValueError:
		raise Http404()	
	regpools = DHCP_ip_pool.objects.get(id = ip_id)
	regpools.ip1 = str(IPAddress(regpools.ip_first))
	regpools.ip2 = str(IPAddress(regpools.ip_last))
	return  render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regpools})

#Delete a single IP range on the DHCP IP pool model
@login_required
def dhcp_page_IP_range_delete(request, ip_id):
	try:
		ip_id = int(ip_id)
	except ValueError:
		raise Http404()	
	
	mDelete = list()
	mDelete.append(DeleteAndLogRecord(ip_id, DHCP_ip_pool, request.user.username, 'DHCP_ip_pool', ''))
	mlength = len(mDelete)

	return render_to_response('qmul_dhcp_delete_IP_range.html',{'machines':mDelete, 'mlength':mlength})

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
			valAft = { 	'ip_first' :info['IP_range1'], 'ip_last':info['IP_range2'],
					'description' :info['dscr']	}
			modID = EditAndLogRecord('DHCP_ip_pool', ip_id,  DHCP_ip_pool,request.user.username, valAft)
			regpool = DHCP_ip_pool.objects.get(id = modID)
			regpool.ip1 = str(IPAddress(regpool.ip_first))
			regpool.ip2 = str(IPAddress(regpool.ip_last))
			return render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regpool})
	else:
		regmachine = DHCP_ip_pool.objects.get(id = ip_id)		
		editform = Register_IP_range_Form(initial = {'IP_range1':str(IPAddress(regmachine.ip_first)),'IP_range2':str(IPAddress(regmachine.ip_last)),'dscr':regmachine.description})	
	return render_to_response('qmul_dhcp_edit_IP_range.html', {'form':editform, 'ip_id': ip_id})

#################################################################################
####################### DHCP Machine Registration ###############################
#################################################################################
	
#
@login_required
def dhcp_page_listings(request):
	registeredmachines =  DHCP_machine.objects.all().order_by("ip_address")
	return render_to_response('qmul_dhcp_listings.html', {'machinelists' : registeredmachines, 'viewmachine' : 'qmul_dhcp_viewmachine.html' })	

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
			valAft = { 	'mac_address' :info['mcID'],'ip_address':info['ipID'],
					'host_name' :info['pcID'],'description' :info['dscr']	}
			modID = EditAndLogRecord('DHCP_machine', m_id,  DHCP_machine,request.user.username, valAft)
			regmachine = DHCP_machine.objects.get(id = modID)
			regmachine.ip = str(IPAddress(regmachine.ip_address))
			return render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine})
	else:
		regmachine = DHCP_machine.objects.get(id = m_id)		
		editform = RegisterMachineForm(initial = {'mcID':regmachine.mac_address,'ipID':str(IPAddress(regmachine.ip_address)), 'pcID':regmachine.host_name,'dscr':regmachine.description})		
	return render_to_response('qmul_dhcp_editmachine.html', {'form':editform, 'm_id': m_id})

#
@login_required
def dhcp_page_machine_delete_multiple(request):	
	registeredmachines =  DHCP_machine.objects.all().order_by("ip_address")
	#for display purposes
	for i in range(len(registeredmachines)):
		registeredmachines[i].ip = str(IPAddress(registeredmachines[i].ip_address))
	if request.method == 'POST':
		actionForm = ViewMachinesActionForm(request.POST)		
		action = request.POST['status']
		if actionForm.is_valid():
			item_selected = request.POST.getlist('cbox_id')
			if item_selected:			
				if action == 'del':
					mDelete = list()
					c_user = request.user.username
					for item in item_selected:
						mDelete.append(DeleteAndLogRecord(item, DHCP_machine, c_user, 'DHCP_machine', ''))
					mlength = len(mDelete)
					return render_to_response('qmul_dhcp_deletemachine.html',{'machines':mDelete, 'mlength':mlength})
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						return render_to_response('qmul_dhcp_listings.html', {'form':actionForm, 'machinelists' : registeredmachines })
					else:
						regmachine = DHCP_machine.objects.get(id = item_selected[0])
						return render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine})
				else:
					actionForm = ViewMachinesActionForm(initial = {})
					return render_to_response('qmul_dhcp_listings.html',{'form':actionForm, 'machinelists' : registeredmachines })	
			else:		
				actionForm = ViewMachinesActionForm(initial = {})
				return render_to_response('qmul_dhcp_listings.html',{'form':actionForm, 'machinelists' : registeredmachines })	
	else:
		actionForm = ViewMachinesActionForm(initial = {})
		return render_to_response('qmul_dhcp_listings.html',{'form':actionForm, 'machinelists' : registeredmachines})

#Delete a single record in the DHCP registration model
@login_required
def dhcp_page_machine_delete_single(request, m_id):
	try:
		m_id = int(m_id)
	except ValueError:
		raise Http404()	
	
	mDelete = list()
	mDelete.append(DeleteAndLogRecord(m_id, DHCP_machine, request.user.username, 'DHCP_machine', ''))
	mlength = len(mDelete)
	
	return render_to_response('qmul_dhcp_deletemachine.html',{'machines':mDelete, 'mlength':mlength})

#View a single registered machine in the DHCP model
@login_required
def dhcp_page_machine_view(request, m_id):
	try:
		m_id = int(m_id)
	except ValueError:
		raise Http404()	
	regmachine = DHCP_machine.objects.get(id = m_id)
	regmachine.ip = str(IPAddress(regmachine.ip_address))
	return  render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine})

#Add a machine to the DHCP registration model
@login_required	
def dhcp_page_machine_add(request):
	if request.method == 'POST':
		form = RegisterMachineForm(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			values = { 	'mac_address' :info['mcID'],'ip_address' :info['ipID'],
					'host_name'  :info['pcID'],'description':info['dscr'] }
			registeredID = AddAndLogRecord('DHCP_machine',  DHCP_machine, request.user.username, values)
			machine_registered  = DHCP_machine.objects.get(id = registeredID)
			machine_registered.ip = str(IPAddress(machine_registered.ip_address))
			return render_to_response('qmul_dhcp_viewmachine.html', {'machine': machine_registered})
	else:
		form = RegisterMachineForm(initial = {})
		
	return render_to_response('qmul_dhcp_createmachine.html', {'form':form })
	
