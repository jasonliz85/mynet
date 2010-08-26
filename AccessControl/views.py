from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict
from mynet.AccessControl.models import *
from mynet.AccessControl.forms import *
from mynet.HistoryLog.models import *
from mynet.HistoryLog.views import *

#RegisterMachineForm, ViewMachinesActionForm, Register_IP_range_Form, Register_namepair_Form 

from IPy import IP
from netaddr import *
from django.utils.html import escape 

import django.forms as forms 
import datetime, json, difflib

class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'
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
		values: m_id = unique id of record in db, model_name = name of the table in db
	"""
	#initialize values
	now = datetime.datetime.today()
	is_modified = bool(0)
	mod_record = model_name.objects.get(id = m_id)
	valBef = mod_record.LogRepresentation()
	t_number = get_table_number(m_name_str)
	#switch to appropriete model and deal with each slightly differently
	if m_name_str == "DNS_names":	
		if not mod_record.machine_name == values['machine_name']: 
			mod_record.machine_name = values['machine_name']
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
		if not mod_record.ip_pair == str(IPAddress(values['ip_pair'])):
			mod_record.ip_pair = str(IPAddress(values['ip_pair']))
			is_modified = bool(1)
			if (IPAddress(values['ip_pair']).version == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			mod_record.is_ipv6 = ipVersion		
	elif m_name_str == "DHCP_ip_pool":
		if not mod_record.IP_pool1 == str(IPAddress(values['IP_pool1'])):
			if (IPAddress(values['IP_pool1']).version == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			is_modified = bool(1)
			mod_record.IP_pool1 = str(IPAddress(values['IP_pool1']))
			mod_record.is_ipv6 = ipVersion
		if not mod_record.IP_pool2 == str(IPAddress(values['IP_pool2'])):
			mod_record.IP_pool2 = str(IPAddress(values['IP_pool2']))
			is_modified = bool(1)
		if not mod_record.description == values['description']:
			if CompareDescriptions(mod_record.description, values['description']):
				mod_record.description = values['description']
				is_modified = bool(1)
	elif m_name_str == "DHCP_machine":
		if not mod_record.MAC_pair == str(EUI(values['MAC_pair'], dialect=mac_custom)):
			mod_record.MAC_pair = str(EUI(values['MAC_pair'], dialect=mac_custom))
			is_modified = bool(1)
		if not mod_record.IP_pair == str(IPAddress(values['IP_pair'])):
			mod_record.IP_pair = str(IPAddress(values['IP_pair']))
			is_modified = bool(1)
		if not mod_record.PC_pair == values['PC_pair']:
			mod_record.PC_pair = values['PC_pair']
			is_modified = bool(1)
		if not mod_record.description == values['description']:
			if CompareDescriptions(mod_record.description, values['description']):
				mod_record.description = values['description']
				is_modified = bool(1)
	else: 
		return bool(0)
	if is_modified:		
		final_values = str(values)
		init_values = str(valBef)
		mod_record.save()
		LogEvent('E',init_values, final_values, False, uname, "NetGroup:ToDo", t_number, m_id)
		
	return mod_record.id

	
def AddAndLogRecord(m_name_str, model_name, uname, values):
	"""
	This function adds a Record in the database and logs the event in the HistoryLog db.
	"""
	now = datetime.datetime.today()
	t_number = get_table_number(m_name_str)
	if m_name_str == "DNS_names":
		if (IPAddress(values['ip_pair']).version == 6):
			ipVersion = bool(1)
		else:
			ipVersion = bool(0)
		tp = values['dns_typ']
		if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
			tp = '1BD'
		newRecord = model_name( machine_name	= values['machine_name'],
					ip_pair		= str(IPAddress(values['ip_pair'])),
					dns_type	= tp,
					is_active 	= bool(1),
					is_ipv6 	= ipVersion,
					time_created 	= now,
					description 	= values['description']								
					)
	elif m_name_str == "DHCP_ip_pool":		
		if (IPAddress(values['IP_pool1']).version == 6):
			ipVersion = bool(1)
		else:
			ipVersion = bool(0)				
		newRecord = model_name(	IP_pool1	= str(IPAddress(values['IP_pool1'])),
					IP_pool2	= str(IPAddress(values['IP_pool2'])),
					is_active 	= bool(1),
					is_ipv6 	= ipVersion,
					time_created 	= now,
					description 	= values['description']								
					)
	elif m_name_str == "DHCP_machine":
		newRecord = model_name(	MAC_pair = str(EUI(values['MAC_pair'], dialect=mac_custom)),
					IP_pair	= str(IPAddress(values['IP_pair'])),
					PC_pair = values['PC_pair'],
					time_created = now,
					description = values['description']
					)
	else: 
		return bool(0)
	newRecord.save() #vals = model_name.objects.filter(id = newRecord.id).values() 
	init_values = "{}" 
	final_values = newRecord.LogRepresentation()#str(vals[0])
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
#DHCP_ip_pool
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
	ip_pair = original_machine.ip_pair
	mn_pair = original_machine.machine_name
	if request.method == "POST":
		form = addForm(request.POST)
		if form.is_valid():
			try:
				newObject = form.cleaned_data #form.save()
			except forms.ValidationError, error:
				newObject = None
			if newObject:
				values = { 	'machine_name' :newObject['service_name'],'dns_typ' :"2NA",
						'ip_pair' :original_machine.ip_pair,'description':newObject['dscr'] }
				AddAndLogRecord('DNS_names', DNS_names, request.user.username, values)					
				display = "Added " + " " + newObject['service_name']
				return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script> <p>Test to display.</p>' %\
					(newObject, display )) #._get_pk_val()
	else:		
		form = addForm(initial = {})
	
	pageContext = {'form': form, 'field': field, 'mach':mn_pair, 'ip':ip_pair}
	return render_to_response("qmul_dns_create_simple.html", pageContext)

#Add an IP-name pair to modelquery set
@login_required
def dns_namepair_add(request):
	if request.method == 'POST':
		form = Register_namepair_Form(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			values = { 	'machine_name' :info['dns_expr'],'dns_typ' :info['dns_typ'],
					'ip_pair' :info['ip_pair'],'description':info['dscr'] }
			registeredID = AddAndLogRecord('DNS_names', DNS_names, request.user.username, values)
			add_service = request.POST.getlist('service_add')
			if add_service:
				#		
				for item in add_service:
					service_add = eval(item)
					values = { 	'machine_name':service_add['dns_expr'],'dns_typ':service_add['dns_typ'],
							'ip_pair':service_add['ip_pair'],'description':service_add['dscr'] }
					AddAndLogRecord('DNS_names', DNS_names, request.user.username, values)			
			regServices = DNS_names.objects.filter(ip_pair = info['ip_pair']).exclude(id = registeredID)
			namepair_registered  = DNS_names.objects.get(id = registeredID)
			return render_to_response('qmul_dns_view_namepair.html', {'machine': namepair_registered, 'machinelists':regServices})
	else:
		form = Register_namepair_Form(initial = {})
	return render_to_response('qmul_dns_create_namepair.html',{'form':form })

#list all ip-name records in the model
@login_required
def dns_namepair_listing(request):
	registered_pairs =  DNS_names.objects.all()#.order_by("dns_type")
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
						mDelete.append(DeleteAndLogRecord(item, DNS_names, c_user, 'DNS_names'))
					mlength = len(mDelete)
					return render_to_response('qmul_dns_delete_namepair.html',{'machines':mDelete, 'mlength' : mlength})
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						return render_to_response('qmul_dns_listings_namepair.html', {'form':actionForm, 'machinelists' : registered_pairs })
					else:
						regmachine = DNS_names.objects.get(id = item_selected[0])
						regServices = DNS_names.objects.filter(ip_pair = regmachine.ip_pair).exclude(id = regmachine.id)
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
	regServices = DNS_names.objects.filter(ip_pair = regpair.ip_pair).exclude(id = regpair.id)
	return  render_to_response('qmul_dns_view_namepair.html', {'machine': regpair, 'machinelists': regServices})

#delete a single record 
@login_required
def dns_namepair_delete(request, pair_id):
	try:
		pair_id = int(pair_id)
	except ValueError:
		raise Http404()		
	mDelete = list()
	mDelete.append(DeleteAndLogRecord(pair_id, DNS_names, request.user.username, 'DNS_names'))
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
			valAft = { 	'machine_name' :info['dns_expr'],'dns_type':info['dns_typ'],
					'ip_pair' :info['ip_pair'],'description' :info['dscr']	}
			modID = EditAndLogRecord('DNS_names', pair_id,  DNS_names,request.user.username, valAft)
			regpair = DNS_names.objects.get(id = modID)
			regServices = DNS_names.objects.filter(ip_pair = regpair.ip_pair).exclude(id = modID)
			return render_to_response('qmul_dns_view_namepair.html', {'machine': regpair, 'machinelists':regServices})
	else:
		regpair = DNS_names.objects.get(id = pair_id)		
		editform = Register_namepair_Form(initial = {'dns_expr':regpair.machine_name,'ip_pair':regpair.ip_pair,'dscr':regpair.description, 'dns_typ': regpair.dns_type})	
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
			values = { 	'IP_pool1' :info['IP_range1'],'IP_pool2' :info['IP_range2'],
					'description':info['dscr'] }
			registeredID = AddAndLogRecord('DHCP_ip_pool',  DHCP_ip_pool, request.user.username, values)
			IP_pool_registered  = DHCP_ip_pool.objects.get(id = registeredID)					
			return render_to_response('qmul_dhcp_view_IP_range.html', {'machine': IP_pool_registered})
	else:
		form = Register_IP_range_Form(initial = {})

	return render_to_response('qmul_dhcp_create_IP_range.html',{'form':form })
#List all IP range records in the DHCP IP pool model
@login_required
def dhcp_page_IP_range_listing(request):
	registered_IP_pools =  DHCP_ip_pool.objects.all().order_by("IP_pool1")
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
						mDelete.append(DeleteAndLogRecord(item, DHCP_ip_pool, c_user, 'DHCP_ip_pool'))
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
	return  render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regpools})

#Delete a single IP range on the DHCP IP pool model
@login_required
def dhcp_page_IP_range_delete(request, ip_id):
	try:
		ip_id = int(ip_id)
	except ValueError:
		raise Http404()	
	
	mDelete = list()
	mDelete.append(DeleteAndLogRecord(ip_id, DHCP_ip_pool, request.user.username, 'DHCP_ip_pool'))
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
			valAft = { 	'IP_pool1' :info['IP_range1'], 'IP_pool2':info['IP_range2'],
					'description' :info['dscr']	}
			modID = EditAndLogRecord('DHCP_ip_pool', ip_id,  DHCP_ip_pool,request.user.username, valAft)
			regpool = DHCP_ip_pool.objects.get(id = modID)
			return render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regpool})
	else:
		regmachine = DHCP_ip_pool.objects.get(id = ip_id)		
		editform = Register_IP_range_Form(initial = {'IP_range1':regmachine.IP_pool1,'IP_range2':regmachine.IP_pool2,'dscr':regmachine.description})	
	return render_to_response('qmul_dhcp_edit_IP_range.html', {'form':editform, 'ip_id': ip_id})

#################################################################################
####################### DHCP Machine Registration ###############################
#################################################################################
	
#
@login_required
def dhcp_page_listings(request):
	registeredmachines =  DHCP_machine.objects.all().order_by("IP_pair")
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
			valAft = { 	'MAC_pair' :info['mcID'],'IP_pair':info['ipID'],
					'PC_pair' :info['pcID'],'description' :info['dscr']	}
			modID = EditAndLogRecord('DHCP_machine', m_id,  DHCP_machine,request.user.username, valAft)
			regmachine = DHCP_machine.objects.get(id = modID)
			return render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine})
	else:
		regmachine = DHCP_machine.objects.get(id = m_id)		
		editform = RegisterMachineForm(initial = {'mcID':regmachine.MAC_pair,'ipID':regmachine.IP_pair, 									'pcID':regmachine.PC_pair,'dscr':regmachine.description})		
	return render_to_response('qmul_dhcp_editmachine.html', {'form':editform, 'm_id': m_id})

#
@login_required
def dhcp_page_machine_delete_multiple(request):	
	registeredmachines =  DHCP_machine.objects.all().order_by("IP_pair")
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
						mDelete.append(DeleteAndLogRecord(item, DHCP_machine, c_user, 'DHCP_machine'))
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
	mDelete.append(DeleteAndLogRecord(m_id, DHCP_machine, request.user.username, 'DHCP_machine'))
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
	return  render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine})

#Add a machine to the DHCP registration model
@login_required	
def dhcp_page_machine_add(request):
	if request.method == 'POST':
		form = RegisterMachineForm(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			values = { 	'MAC_pair' :info['mcID'],'IP_pair' :info['ipID'],
					'PC_pair'  :info['pcID'],'description':info['dscr'] }
			registeredID = AddAndLogRecord('DHCP_machine',  DHCP_machine, request.user.username, values)
			machine_registered  = DHCP_machine.objects.get(id = registeredID)
			return render_to_response('qmul_dhcp_viewmachine.html', {'machine': machine_registered})
	else:
		form = RegisterMachineForm(initial = {})
		
	return render_to_response('qmul_dhcp_createmachine.html', {'form':form })
	
