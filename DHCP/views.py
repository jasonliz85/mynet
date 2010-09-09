from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from mynet.DHCP.models import *

from mynet.DHCP.forms import *

from mynet.views import *
from mynet.helper_views import *

from netaddr import *
import datetime

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
			regmachine.ip = IPAddress(regmachine.ip_address)
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
	
