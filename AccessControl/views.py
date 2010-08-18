from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict
from mynet.AccessControl.models import *
from mynet.HistoryLog.models import *
from mynet.HistoryLog.views import LogEvent
from mynet.AccessControl.forms import * 
#RegisterMachineForm, ViewMachinesActionForm, Register_IP_range_Form, Register_namepair_Form 

from IPy import IP
from netaddr import *
from django.utils.html import escape 

import django.forms as forms 
import datetime

class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'

def EditAndLogRecord(m_id, model_name): 
	"""
	This function edits a Record in the database and logs the event in the HistoryLog db
		values: m_id = unique id of record in db, model_name = name of the table in db
	"""
	return
	
def AddAndLogRecord(m_id, model_name):
	"""
	This function adds a Record in the database and logs the event in the HistoryLog db
		values: m_id = unique id of record in db, model_name = name of the table in db
	"""
	return 
	
def DeleteAndLogRecord(m_id, Model_Name, request):
	"""
	This function deletes a Record in the database and logs the event in the HistoryLog db. It returns 
	a list of the fields and values that were deleted.
		values: m_id = unique id of record in db, model_name = name of the table in db
	"""
	returnRecordList = []
	DeleteRecord = Model_Name.objects.filter(id = m_id) 
	vals = DeleteRecord.values()
	init_values = str(vals[0])
	final_values = ""
	uname = request.user.username
	returnRecordList.append(DeleteRecord)
	DeleteRecord.delete()
	LogEvent('D',init_values, final_values, False, uname, "")
		
	return DeleteRecord
	#vals = u'{\'machine_name\':\'%s\',\'ip_pair\':\'%s\',\'is_ipv6\':\'%s\',\'dns_type\':\'%s\',\'description\':\'%s\'}' % (DeleteRecord.machine_name, DeleteRecord.ip_pair, DeleteRecord.is_ipv6, DeleteRecord.dns_type, DeleteRecord.description)
	
#################################################################################
####################### DNS NAME Pair ###########################################
#################################################################################

#
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
				newObject = form.cleaned_data#form.save()
			except forms.ValidationError, error:
				newObject = None
			if newObject:
				now = datetime.datetime.today()
				newService = DNS_names(machine_name	= newObject['service_name'],
							ip_pair		= original_machine.ip_pair,
							dns_type	= "2NA",
							is_active 	= bool(1),
							is_ipv6 	= original_machine.is_ipv6,
							time_created 	= now,
							description 	= newObject['dscr']								
							)
				newService.save()					
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
			now = datetime.datetime.today()
			info = form.cleaned_data
			if (IPAddress(info['ip_pair']).version == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			tp = request.POST['dns_typ']
			if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
				tp = '1BD'
			namepair_registered = DNS_names(machine_name	= info['dns_expr'],
							ip_pair		= str(IPAddress(info['ip_pair'])),
							dns_type	= tp,
							is_active 	= bool(1),
							is_ipv6 	= ipVersion,
							time_created 	= now,
					#vals = u'{\'machine_name\':\'%s\',\'ip_pair\':\'%s\',\'is_ipv6\':\'%s\',\'dns_type\':\'%s\',\'description\':\'%s\'}' % (DeleteRecord.machine_name, DeleteRecord.ip_pair, DeleteRecord.is_ipv6, DeleteRecord.dns_type, DeleteRecord.description)		description 	= info['dscr']								
							)		
			namepair_registered.save()
			add_service = request.POST.getlist('service_add')
			if add_service:
				#		
				for item in add_service:
					service_add = eval(item)
					if (IPAddress(service_add['ip_pair']).version == 6):
						ipVersion = bool(1)
					else:
						ipVersion = bool(0)
					tp = service_add['dns_typ']
					if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
						tp = '1BD'
					registered_services = DNS_names( machine_name	= service_add['dns_expr'],
									ip_pair		= str(IPAddress(service_add['ip_pair'])),
									dns_type	= tp,
									is_active 	= bool(1),
									is_ipv6 	= ipVersion,
									time_created 	= now,
									description 	= service_add['dscr']								
									)
					registered_services.save()			
					
			regServices = DNS_names.objects.filter(ip_pair = namepair_registered.ip_pair).exclude(id = namepair_registered.id)	
			return render_to_response('qmul_dns_view_namepair.html', {'machine': namepair_registered, 'machinelists':regServices})
	else:
		form = Register_namepair_Form(initial = {})
	return render_to_response('qmul_dns_create_namepair.html',{'form':form })

#list all ip-name records in the model
@login_required
def dns_namepair_listing(request):
	registered_pairs =  DNS_names.objects.all()#.order_by("dns_type")
	if request.method == 'POST':
		actionForm = ViewMachinesAction(request.POST)	
		action = request.POST['status']
		if actionForm.is_valid():
			item_selected = request.POST.getlist('cbox_id')
			if item_selected:			
				if action == 'del':
					mDelete = []
					for item in item_selected:		
						mDelete.append(DNS_names.objects.get(id = item))
						DNS_names.objects.get(id = item).delete()
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
	mDelete = []
	mDelete.append(DeleteAndLogRecord(pair_id, DNS_names, request))
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
			regpair = DNS_names.objects.get(id = pair_id)
			regpair.machine_name	= info['dns_expr']
			regpair.ip_pair		= str(IPAddress(info['ip_pair']))
			regpair.description	= info['dscr']
			if (IPAddress(info['ip_pair']) == 6):
				regpair.is_ipv6 = bool(1)
			else:
				regpair.is_ipv6 = bool(0)
			now = datetime.datetime.today()
			regpair.time_modified = now
			regpair.save()
			regServices = DNS_names.objects.filter(ip_pair = regpair.ip_pair).exclude(id = regpair.id)
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
			now = datetime.datetime.today()
			info = form.cleaned_data
			if (IPAddress(info['IP_range1']).version == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)				
			IP_pool_registered = DHCP_ip_pool(	IP_pool1	= str(IPAddress(info['IP_range1'])),
								IP_pool2	= str(IPAddress(info['IP_range2'])),
								is_active 	= bool(1),
								is_ipv6 	= ipVersion,
								time_created 	= now,
								description 	= info['dscr']								
								)		
			IP_pool_registered.save()					
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
					mDelete = []
					for item in item_selected:		
						mDelete.append(DHCP_ip_pool.objects.get(id = item))
						DHCP_ip_pool.objects.get(id = item).delete()
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
	now = datetime.datetime.today()
	mDelete = []
	DeleteRecord = DHCP_ip_pool.objects.get(id = ip_id)
	mDelete.append(DeleteRecord)	
	mlength = len(mDelete)
	DeleteRecord.delete()
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
			regpool = DHCP_ip_pool.objects.get(id = ip_id)
			regpool.IP_pool1	= str(IPAddress(info['IP_range1']))
			regpool.IP_pool2	= str(IPAddress(info['IP_range2']))
			regpool.description	= info['dscr']
			if (IPAddress(info['IP_range1']).version == 6):
				regpool.is_ipv6 = bool(1)
			else:
				regpool.is_ipv6 = bool(0)
			now = datetime.datetime.today()
			regpool.time_modified = now
			regpool.save()
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
			regmachine = DHCP_machine.objects.get(id = m_id)
			regmachine.MAC_pair 	= str(EUI(info['mcID'], dialect=mac_custom))
			regmachine.IP_pair	= str(IPAddress(info['ipID']))
			regmachine.PC_pair	= info['pcID']
			regmachine.description	= info['dscr']
			regmachine.save()
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
					mDelete = []
					for item in item_selected:		
						mDelete.append(DHCP_machine.objects.get(id = item))
						DHCP_machine.objects.get(id = item).delete()
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
	now = datetime.datetime.today()
	mDelete = []
	mDelete.append(DHCP_machine.objects.get(id = m_id))	
	DHCP_machine.objects.get(id = m_id).delete()
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
			now = datetime.datetime.today()
			info = form.cleaned_data			
			machine_registered = DHCP_machine(	MAC_pair = str(EUI(info['mcID'], dialect=mac_custom)),
								IP_pair	= str(IPAddress(info['ipID'])),
								PC_pair = info['pcID'],
								time_created = now,
								description = info['dscr']
								)
		
			machine_registered.save()					
			return render_to_response('qmul_dhcp_viewmachine.html', {'machine': machine_registered})
	else:
		form = RegisterMachineForm(initial = {})
		
	return render_to_response('qmul_dhcp_createmachine.html', {'form':form })
	
