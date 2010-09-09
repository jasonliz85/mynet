from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
#import models
from mynet.DNS.models import *
#import forms
from mynet.DNS.forms import *
#import views
from mynet.AccessControl.views import *
from mynet.views import *
from mynet.helper_views import *

from netaddr import *
import datetime

#################################################################################
####################### DNS NAME Pair ###########################################
#################################################################################
#DNS_name pair
@login_required
def dns_namepair_simpleAdd(request, pair_id):
	try:
		pair_id = int(pair_id)
	except ValueError:
		raise Http404()	
	return handlePopAdd(request, Register_service_Form, 'services', pair_id)
	
#handle pop_up
def handlePopAdd(request, addForm, field, original_id):
	original_machine = DNS_name.objects.get(id = original_id)
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
					AddAndLogRecord('DNS_name', DNS_name, request.user.username, values)					
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
				registeredID = AddAndLogRecord('DNS_name', DNS_name, request.user.username, values)
				namepair_registered  = DNS_name.objects.get(id = registeredID)
				namepair_registered.ip = str(IPAddress(namepair_registered.ip_address))
				add_service = request.POST.getlist('service_add')
				#if add_service parameter is triggered, will add the item to the model db
				if add_service:		
					for item in add_service:
						service_add = eval(item)
						values = { 	'name':service_add['dns_expr'],'dns_typ':service_add['dns_typ'],
								'ip_address':int(IPAddress(service_add['ip_address'])),'description':service_add['dscr'] }
						AddAndLogRecord('DNS_name', DNS_name, request.user.username, values)			
				#find all other associated services and display them
				tempFilter = DNS_name.objects.filter(ip_address = int(IPAddress(info['ip_address']))).exclude(id = registeredID)
				regServices = list()
				for i in range(len(tempFilter)):
					[is_service_permitted, msg] = dns_permission_check(request,int(IPAddress(tempFilter[i].ip_address)), tempFilter[i].name, tempFilter[i].dns_type)
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
	
	registered_pairs =  dns_get_permited_records(request, True)# DNS_name.objects.all()#.order_by("dns_type")
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
						mDelete.append(DeleteAndLogRecord(item, DNS_name, c_user, 'DNS_name', ''))
					mlength = len(mDelete)
					return render_to_response('qmul_dns_delete_namepair.html',{'machines':mDelete, 'mlength' : mlength})
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						return render_to_response('qmul_dns_listings_namepair.html', {'form':actionForm, 'machinelists' : registered_pairs })
					else:
						regmachine = DNS_name.objects.get(id = item_selected[0])
						regServices = DNS_name.objects.filter(ip_address = regmachine.ip_address).exclude(id = regmachine.id)
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
	regpair = DNS_name.objects.get(id = pair_id)
	regpair.ip = str(IPAddress(regpair.ip_address))
	#regServices = DNS_name.objects.filter(ip_pair = regpair.ip_pair).exclude(id = regpair.id)
	#for i in range(len(regServices)):
	#	regServices[i].ip = str(IPAddress(regServices[i].ip_pair))
		
	tempFilter = DNS_name.objects.filter(ip_address = regpair.ip_address).exclude(id = regpair.id)
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
	mDelete.append(DeleteAndLogRecord(pair_id, DNS_name, request.user.username, 'DNS_name', ''))
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
				modID = EditAndLogRecord('DNS_name', pair_id,  DNS_name,request.user.username, valAft)
				regpair = DNS_name.objects.get(id = modID)
				regpair.ip = str(IPAddress(regpair.ip_address))
				regServices = DNS_name.objects.filter(ip_address = regpair.ip_address).exclude(id = modID)
				for i in range(len(regServices)):
					regServices[i].ip = str(IPAddress(regServices[i].ip_address))
		
				return render_to_response('qmul_dns_view_namepair.html', {'machine': regpair, 'machinelists':regServices})
			else:
				form = Register_namepair_Form(initial = {'dns_expr':info['dns_expr'],'dns_typ':info['dns_typ'],'ip_address':info['ip_address'],'dscr':info['dscr']})
				return render_to_response('qmul_dns_create_namepair.html',{'form':form ,'c_errors': custom_errors })
	else:
		regpair = DNS_name.objects.get(id = pair_id)		
		editform = Register_namepair_Form(initial = {'dns_expr':regpair.name,'ip_address':str(IPAddress(regpair.ip_address)),'dscr':regpair.description, 'dns_typ': regpair.dns_type})	
	return render_to_response('qmul_dns_edit_namepair.html', {'form':editform, 'ip_id': pair_id})
