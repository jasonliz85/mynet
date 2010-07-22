from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, QueryDict
from mynet.AccessControl.models import DHCP_machine, test_machine
from mynet.AccessControl.forms import RegisterMachineForm, EditRegisteredMachineForm, ViewMachinesActionForm, ViewMachinesForm
from django.forms.formsets import formset_factory
from IPy import IP
import datetime

#################################################################################
####################### DHCP IP Pool ############################################
#################################################################################

#Add a IP range to the DHCP IP pool model
@login_required
def dhcp_page_IP_range_add(request):
	return render_to_response('qmul_dhcp_create_IP_range.html',{})

#Viw a single IP range record on the DHCP IP pool model
@login_required
def dhcp_page_IP_range_view(request, ip_id):
	return render_to_response('qmul_dhcp_view_IP_range.html',{})

#Delete a single IP range on the DHCP IP pool model
@login_required
def dhcp_page_IP_range_delete(request):
	return render_to_response('qmul_dhcp_delete_IP_range.html',{})

#Edit a single IP range to the DHCP IP pool model
@login_required
def dhcp_page_IP_range_edit(request):
	return render_to_response('qmul_dhcp_edit_IP_range.html',{})

#List all IP range records in the DHCP IP pool model
@login_required
def dhcp_page_IP_range_listing(request):
	return render_to_response('qmul_dhcp_listings_IP_range.html',{})

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
		editform = EditRegisteredMachineForm(request.POST)
		if editform.is_valid():
			info = editform.cleaned_data
			regmachine = DHCP_machine.objects.get(id = m_id)
			regmachine.MAC_pair 	= info['mcID']
			regmachine.IP_pair	= info['ipID']
			regmachine.PC_pair	= info['pcID']
			regmachine.description	= info['dscr']
			regmachine.save()
			return render_to_response('qmul_dhcp.html', {})
	else:
		regmachine = DHCP_machine.objects.get(id = m_id)		
		editform = EditRegisteredMachineForm(initial = {'mcID':regmachine.MAC_pair,'ipID':regmachine.IP_pair, 									'pcID':regmachine.PC_pair,'dscr':regmachine.description})		
	return render_to_response('qmul_dhcp_editmachine.html', {'form':editform, 'm_id': m_id})

#
@login_required
def dhcp_page_list_machines(request):
	ViewMachinesFormSet = formset_factory(ViewMachinesForm)
	if request.method == 'POST':
		mDelete = []
		return render_to_response('qmul_dhcp_deletemachine.html',{'machines':mDelete})
	else:
		now = datetime.datetime.today()
		regmachine =  DHCP_machine.objects.all().order_by("IP_pair")
		m_form = ViewMachinesFormSet( {		'form-TOTAL_FORMS': u'1',
							'form-INITIAL_FORMS': u'0',
							'form-MAX_NUM_FORMS': u'',
							'form-0-mcID':		'AABBCCDDEEFF',#regmachine.MAC_pair,
							'form-0-ipID':		'192.168.0.0',#regmachine.IP_pair,
							'form-0-pcID':		'asdasd',#regmachine.PC_pair,
							'form-0-date_created':	now #regmachine.date_created
						})
		if m_form.is_valid():
			status = 'yes'
		else:
			status = 'no'
		return render_to_response('qmul_dhcp_listings.html',{'formset': m_form, 'mc':status })

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
					return render_to_response('qmul_dhcp_deletemachine.html',{'machines':mDelete})
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
	#mDelete = DHCP_machine(time_deleted = now)
	#mDelete.delete()
	return render_to_response('qmul_dhcp_deletemachine.html',{'machines':mDelete})

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
	
