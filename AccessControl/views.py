from django.shortcuts import render_to_response
#from django.core.validators import ValidationError, NON_FIELD_ERRORS
from django.http import HttpResponse
from mynet.AccessControl.models import DHCP_machine, test_machine
from mynet.AccessControl.forms import RegisterMachineForm, EditRegisteredMachineForm
import datetime

def dhcp_page_listings(request):
	registeredmachines =  DHCP_machine.objects.all().order_by("IP_pair")
	return render_to_response('qmul_dhcp_listings.html', {'machinelists' : registeredmachines, 'viewmachine' : 'qmul_dhcp_viewmachine.html' })	
	
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

def dhcp_page_machine_delete(request):
	return render_to_response('qmul_dhcp_deletemachine.html',{})

def dhcp_page_machine_view(request, m_id):
	try:
		m_id = int(m_id)
	except ValueError:
		raise Http404()	
	regmachine = DHCP_machine.objects.get(id = m_id)
	return  render_to_response('qmul_dhcp_viewmachine.html', {'machine': regmachine})
	
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
	
