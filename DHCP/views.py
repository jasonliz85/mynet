from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
#-------import models
from subnets.DHCP.models import *
#-------import forms
from subnets.DHCP.forms import *
#-------import views
from subnets.helper_views import *
#from netaddr import *
import datetime

class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'

#################################################################################
####################### DHCP IP Pool ############################################
#################################################################################
def ParameterChecks(user_object, ip1, ip2, mac, rid, is_ip_pools):
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
		else:
			[is_valid, error_msg] = DHCP_machine.objects.is_unique(user_object.user, ip1, mac, rid)
			
	return is_valid, error_msg
	
#Add a IP range to the DHCP IP pool model
@login_required
def dhcp_page_IP_range_add(request):
	if request.method == 'POST':
		form = Register_IP_range_Form(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			ip_f = IPAddress(info['IP_range1'])
			ip_l = IPAddress(info['IP_range2'])
			[can_pass, custom_errors] = ParameterChecks(request, ip_f, ip_l, "", "", True)
			if can_pass:
				values = { 	'ip_first':ip_f, 'ip_last':ip_l,
						'description':info['dscr'] }
				registeredID = AddAndLogRecord('DHCP_ip_pool',  DHCP_ip_pool, request.user.username, values)
				IP_pool_registered  = DHCP_ip_pool.objects.get(id = registeredID)
				#for display purposes
				IP_pool_registered.ip1 = str(IP_pool_registered.ip_first)
				IP_pool_registered.ip2 = str(IP_pool_registered.ip_last)					
				return render_to_response('qmul_dhcp_view_IP_range.html', {'machine': IP_pool_registered})
			else:
				form = Register_IP_range_Form(initial = { 'IP_range1' :info['IP_range1'],'IP_range2' :info['IP_range2'],'dscr':info['dscr'] })
				return render_to_response('qmul_dhcp_create_IP_range.html',{'form':form ,'c_errors': custom_errors})
	else:
		form = Register_IP_range_Form(initial = {})

	return render_to_response('qmul_dhcp_create_IP_range.html',{'form':form })
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
	#registered_IP_pools = DHCP_ip_pool.objects.get_permitted_records(request)
	registered_IP_pools = DHCP_ip_pool.objects.get_permitted_records(request, order_by, order_dir, change_dir)
	for i in range(len(registered_IP_pools)):#for display purposes
		registered_IP_pools[i].ip1 = str(IPAddress(registered_IP_pools[i].ip_first))
		registered_IP_pools[i].ip2 = str(IPAddress(registered_IP_pools[i].ip_last))
		registered_IP_pools[i].record_no = i + 1
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
					c_user = request.user.username
					for item in item_selected:
						mDelete.append(DeleteAndLogRecord(item, DHCP_ip_pool, c_user, 'DHCP_ip_pool', ''))
					mlength = len(mDelete)
					return render_to_response('qmul_dhcp_delete_IP_range.html',{'machines':mDelete, 'mlength' : mlength})
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						return render_to_response('qmul_dhcp_listings_IP_range.html', {'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort })
					else:
						regmachine = DHCP_ip_pool.objects.get(id = item_selected[0])
						regmachine.ip1 = str(regmachine.ip_first)
						regmachine.ip2 = str(regmachine.ip_last)
						return render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regmachine})
				else:
					actionForm = ViewMachinesActionForm(initial = {})
					return render_to_response('qmul_dhcp_listings_IP_range.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort })	
			else:		
				actionForm = ViewMachinesActionForm(initial = {})
				return render_to_response('qmul_dhcp_listings_IP_range.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort })	
	else:
		actionForm = ViewMachinesActionForm(initial = {})
		return render_to_response('qmul_dhcp_listings_IP_range.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort })
	
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
		regpools.ip1 = str(regpools.ip_first)
		regpools.ip2 = str(regpools.ip_last)
	except DHCP_ip_pool.DoesNotExist:
		return HttpResponseRedirect("/dhcp/pool/list/default")
	#check if permitted
	[is_valid, error_msg] = dhcp_permission_check(request, regpools.ip_first, regpools.ip_last, False)
	if not is_valid:
		return HttpResponseRedirect("/error/permission/")
	return  render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regpools})
	
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
	mDelete.append(DeleteAndLogRecord(ip_id, DHCP_ip_pool, request.user.username, 'DHCP_ip_pool', ''))
	if mDelete == False:
		return HttpResponseRedirect("/dhcp/pool/list/default")
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
			ip_f = IPAddress(info['IP_range1'])
			ip_l = IPAddress(info['IP_range2'])
			[can_pass, custom_errors] = ParameterChecks(request, ip_f, ip_l, "", ip_id, True)
			if can_pass:
				valAft = { 	'ip_first':ip_f, 'ip_last':ip_l,
						'description' :info['dscr']	}
				modID = EditAndLogRecord('DHCP_ip_pool', ip_id,  DHCP_ip_pool,request.user.username, valAft)
				regpool = DHCP_ip_pool.objects.get(id = modID)
				regpool.ip1 = str(regpool.ip_first)
				regpool.ip2 = str(regpool.ip_last)
				return render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regpool})
			else:
				editform = Register_IP_range_Form(initial = { 'IP_range1' :info['IP_range1'],'IP_range2' :info['IP_range2'],'dscr':info['dscr'] })
				return render_to_response('qmul_dhcp_edit_IP_range.html',{'form':editform ,'ip_id': ip_id,'c_errors': custom_errors})
	else:
		try:
			regmachine = DHCP_ip_pool.objects.get(id = ip_id)	
		except DHCP_ip_pool.DoesNotExist:
			return HttpResponseRedirect("/dhcp/pool/list/default")	
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
			ip = IPAddress(info['ipID'])
			[can_pass, custom_errors] = ParameterChecks(request, ip, '', str(EUI(info['mcID'], dialect=mac_custom)), m_id, False)
			if can_pass:
				valAft = { 	'mac_address' :info['mcID'],'ip_address': ip,
						'host_name' :info['pcID'],'description' :info['dscr']	}
				modID = EditAndLogRecord('DHCP_machine', m_id,  DHCP_machine,request.user.username, valAft)
				regmachine = DHCP_machine.objects.get(id = modID)
				regmachine.ip = regmachine.ip_address
				return render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine})
			else:
				editform = RegisterMachineForm(initial = { 'mcID':info['mcID'],'ipID' :info['ipID'],'pcID':info['pcID'],'dscr':info['dscr'] })
				return render_to_response('qmul_dhcp_editmachine.html',{'form':editform ,'m_id': m_id,'c_errors': custom_errors})
	else:
		try:
			regmachine = DHCP_machine.objects.get(id = m_id)		
		except DHCP_machine.DoesNotExist:
			return HttpResponseRedirect("/dhcp/machine/list/")	
		editform = RegisterMachineForm(initial = {'mcID':regmachine.mac_address,'ipID':str(regmachine.ip_address), 'pcID':regmachine.host_name,'dscr':regmachine.description})		
	return render_to_response('qmul_dhcp_editmachine.html', {'form':editform, 'm_id': m_id})

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
	#registeredmachines =  DHCP_machine.objects.get_permitted_records(request) 
	registeredmachines =  DHCP_machine.objects.get_permitted_records(request, order_by, order_dir, change_dir)
	for i in range(len(registeredmachines)): #for display purposes
		registeredmachines[i].ip = str(IPAddress(registeredmachines[i].ip_address))
		registeredmachines[i].record_no = i + 1
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
					c_user = request.user.username
					for item in item_selected:
						mDelete.append(DeleteAndLogRecord(item, DHCP_machine, c_user, 'DHCP_machine', ''))
					mlength = len(mDelete)
					return render_to_response('qmul_dhcp_deletemachine.html',{'machines':mDelete, 'mlength':mlength})
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						return render_to_response('qmul_dhcp_listings.html', {'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort})
					else:
						regmachine = DHCP_machine.objects.get(id = item_selected[0])
						regmachine.ip = str(regmachine.ip_address)
						return render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine})
				else:
					actionForm = ViewMachinesActionForm(initial = {})
					return render_to_response('qmul_dhcp_listings.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort})	
			else:		
				actionForm = ViewMachinesActionForm(initial = {})
				return render_to_response('qmul_dhcp_listings.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort})	
	else:
		actionForm = ViewMachinesActionForm(initial = {})
		return render_to_response('qmul_dhcp_listings.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort})

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
	mDelete.append(DeleteAndLogRecord(m_id, DHCP_machine, request.user.username, 'DHCP_machine', ''))
	if mDelete == False:
		return HttpResponseRedirect("/dhcp/machine/list/")
	mlength = len(mDelete)
	return render_to_response('qmul_dhcp_deletemachine.html',{'machines':mDelete, 'mlength':mlength})

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
		regmachine.ip = str(IPAddress(regmachine.ip_address))
	except DHCP_machine.DoesNotExist:
		return HttpResponseRedirect("/dhcp/machine/list/")
	#check if permitted
	[is_valid, error_msg] = dhcp_permission_check(request, regmachine.ip_address, "", False)
	if not is_valid:
		return HttpResponseRedirect("/error/permission/")
	return  render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine})

#Add a machine to the DHCP registration model
@login_required	
def dhcp_page_machine_add(request):
	if request.method == 'POST':
		form = RegisterMachineForm(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			ip = IPAddress(info['ipID'])
			[can_pass, custom_errors] = ParameterChecks(request, ip, "", str(EUI(info['mcID'], dialect=mac_custom)), "", False)
			if can_pass:
				values = { 	'mac_address' :info['mcID'],'ip_address' :ip,
						'host_name'  :info['pcID'],'description':info['dscr'] }
				registeredID = AddAndLogRecord('DHCP_machine',  DHCP_machine, request.user.username, values)
				machine_registered  = DHCP_machine.objects.get(id = registeredID)
				machine_registered.ip = str(machine_registered.ip_address)
				return render_to_response('qmul_dhcp_viewmachine.html', {'machine': machine_registered})
			else:
				form = RegisterMachineForm(initial = { 'mcID' :info['mcID'],'ipID' :info['ipID'],'pcID':info['pcID'],'dscr':info['dscr'] })
				return render_to_response('qmul_dhcp_createmachine.html',{'form':form ,'c_errors': custom_errors})
	else:
		form = RegisterMachineForm(initial = {})
		
	return render_to_response('qmul_dhcp_createmachine.html', {'form':form })
def dhcp_fetch_pool_data(request):
	'''
	'''
	error = ''
	records = ''
	subnet = request.GET.get('subnet', '')
	if len(subnet) == 0:
		error = 'No subnet defined.'
	else:
		try:
			print subnet
			sb = IPNetwork(subnet)
			records = DHCP_ip_pool.objects.get_records_in_subnet(sb)
		except AddrFormatError:
			error = 'Subnet format error.'
	
	return render_to_response('qmul_dhcp_range_data.txt', {'records':records, 'error':error})
def dhcp_fetch_host_data(request):
	'''
	'''
	error = ''
	records = ''
	subnet = request.GET.get('subnet', '')
	if len(subnet) == 0:
		error = 'No subnet defined.'
	else:
		try:
			sb = IPNetwork(subnet)
			records = DHCP_machine.objects.get_records_in_subnet(sb)
		except AddrFormatError:
			error = 'Subnet format error.'
			
	return render_to_response('qmul_dhcp_host_data.txt', {'records':records, 'error':error})
