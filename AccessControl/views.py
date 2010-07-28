from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict
from mynet.AccessControl.models import DHCP_machine, DHCP_ip_pool, DNS_names, test_machine
from mynet.AccessControl.forms import RegisterMachineForm, ViewMachinesActionForm, Register_IP_range_Form, Register_namepair_Form 

from IPy import IP
from django.utils.html import escape 

import django.forms as forms 
import datetime

#################################################################################
####################### DNS NAME Pair ###########################################
#################################################################################

#
@login_required
def dns_namepair_simpleAdd(request):
	return handlePopAdd(request, Register_namepair_Form, 'services')
#handle pop_up
def handlePopAdd(request, addForm, field):
	if request.method == "POST":
		form = addForm(request.POST)
		if form.is_valid():
			try:
				newObject = form.cleaned_data#form.save()
			except forms.ValidationError, error:
				newObject = None
			if newObject:
				return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>', (escape(newObject), escape(newObject))) #._get_pk_val()
	else:
		form = addForm()
		
	pageContext = {'form': form, 'field': field}
	return render_to_response("qmul_dns_create_simple.html", pageContext)

#Add an IP-name pair to model
@login_required
def dns_namepair_add(request):
	if request.method == 'POST':
		form = Register_namepair_Form(request.POST)
		if form.is_valid():
			now = datetime.datetime.today()
			info = form.cleaned_data
			if (IP(info['ip_pair']).version() == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			tp = request.POST['dns_typ']
			if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
				tp = '1BD'

			namepair_registered = DNS_names(	machine_name	= info['dns_expr'],
								ip_pair		= IP(info['ip_pair']).strNormal(1),
								dns_type	= tp,
								is_active 	= bool(1),
								is_ipv6 	= ipVersion,
								time_created 	= now,
								description 	= info['dscr']								
								)		
			namepair_registered.save()					
			return render_to_response('qmul_dhcp.html', {})
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
						return render_to_response('qmul_dns_view_namepair.html', {'machine': regmachine})
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
	return  render_to_response('qmul_dns_view_namepair.html', {'machine': regpair})

#delete a single record 
@login_required
def dns_namepair_delete(request, pair_id):
	try:
		pair_id = int(pair_id)
	except ValueError:
		raise Http404()		
	now = datetime.datetime.today()
	mDelete = []
	DeleteRecord = DNS_names.objects.get(id = pair_id)
	mDelete.append(DeleteRecord)	
	mlength = len(mDelete)
	DeleteRecord.delete()
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
			regpair.ip_pair		= IP(info['ip_pair']).strNormal(1)
			regpair.description	= info['dscr']
			if (IP(info['ip_pair']).version() == 6):
				regpair.is_ipv6 = bool(1)
			else:
				regpair.is_ipv6 = bool(0)
			now = datetime.datetime.today()
			regpair.time_modified = now
			regpair.save()
			return render_to_response('qmul_dns_view_namepair.html', {'machine': regpair})
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
			if (IP(info['IP_range1']).version() == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)				
			IP_pool_registered = DHCP_ip_pool(	IP_pool1	= IP(info['IP_range1']).strNormal(1),
								IP_pool2	= IP(info['IP_range2']).strNormal(1),
								is_active 	= bool(1),
								is_ipv6 	= ipVersion,
								time_created 	= now,
								description 	= info['dscr']								
								)		
			IP_pool_registered.save()					
			return render_to_response('qmul_dhcp.html', {})
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
			regpool.IP_pool1	= IP(info['IP_range1']).strNormal(1)
			regpool.IP_pool2	= IP(info['IP_range2']).strNormal(1)
			regpool.description	= info['dscr']
			if (IP(info['IP_range1']).version() == 6):
				regpool.is_ipv6 = bool(1)
			else:
				regpool.is_ipv6 = bool(0)
			now = datetime.datetime.today()
			regpool.time_modified = now
			regpool.save()
			return render_to_response('qmul_dhcp_view_IP_range.html', {'machine': regpool})
	else:
		regmachine = DHCP_ip_pool.objects.get(id = ip_id)		
		editform = Register_IP_range_Form(initial = {'IP_range':regmachine.IP_pool,'dscr':regmachine.description})	
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
			regmachine.MAC_pair 	= info['mcID']
			regmachine.IP_pair	= info['ipID']
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
			machine_registered = DHCP_machine(	MAC_pair = info['mcID'],
								IP_pair	= info['ipID'],
								PC_pair = info['pcID'],
								time_created = now,
								description = info['dscr']
								)
		
			machine_registered.save()					
			return render_to_response('qmul_dhcp.html', {})
	else:
		form = RegisterMachineForm(initial = {})
		
	return render_to_response('qmul_dhcp_createmachine.html', {'form':form })
	
