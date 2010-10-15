from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, InvalidPage, EmptyPage
#import models
from subnets.DNS.models import *
#import forms
from subnets.DNS.forms import *
#import views
from subnets.helper_views import *

from netaddr import *
import datetime

#################################################################################
####################### DNS NAME Pair ###########################################
#################################################################################

def ParameterChecks(user_object, ip, name, dt, rid, enable_softcheck):
	"""
	This function calls is_unique and is_permitted dns test and consolidates errors. Returns True if there are no errors
	and return False otherwise. If there are errors, error_msg will contain a message relating to the nature of the error
	Arguments:
		user_object		= request object
		ip			= ip address (in integer format) 
		name			= machine name
		dt			= dns type
		rid			= if present, the id of the record, usually an integer
		enable_softcheck	= if true, enables the softer checks for is_unique dns records
	"""
	is_valid = False
	error_msg = ""
	#[is_valid, error_msg] = dns_permission_check(user_object, ip, name, dt)
	[is_valid, error_msg] = DNS_name.objects.is_permitted(user_object, ip, name, dt)
	if not is_valid:
		return is_valid, error_msg
	else:
		[is_valid, error_msg] = DNS_name.objects.is_unique(ip, name, dt, rid, enable_softcheck)
	#print error_msg
	return is_valid, error_msg

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
					values = { 	'name' :newObject['service_name'],'dns_type' :"2NA",
							'ip_address' :original_machine.ip_address,'description':newObject['dscr'], 'ttl': newObject['ttl'] }
					AddAndLogRecord('DNS_name', DNS_name, request.user.username, values)					
					display = "Added " + " " + newObject['service_name']
					return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script> <p>Test to display.</p>' %\
						(newObject, display )) #._get_pk_val()
				else:
					pageContext = {'form': form, 'field': field, 'mach':mn_pair, 'ip':str(ip_address),'c_errors': custom_errors}
					return render_to_response("qmul_dns_create_simple.html", pageContext)
	else:		
		form = addForm(initial = {})
	
	pageContext = {'form': form, 'field': field, 'mach':mn_pair, 'ip':str(ip_address) }
	return render_to_response("qmul_dns_create_simple.html", pageContext)

#Add an IP-name pair to modelquery set
@login_required
def dns_namepair_add(request):
	if request.method == 'POST':
		form = Register_namepair_Form(request.POST) 
		if form.is_valid():
			info = form.cleaned_data
			ip = IPAddress(info['ip_address'])
			[can_pass, custom_errors] = ParameterChecks(request, ip, info['dns_expr'], info['dns_type'], '', True)
			#check if this form is permitted first
			if can_pass:
				values = { 	'name' :info['dns_expr'],'dns_type' :info['dns_type'],
						'ip_address' :ip, 'description':info['dscr'], 'ttl': info['ttl'] }
				registeredID = AddAndLogRecord('DNS_name', DNS_name, request.user.username, values)
				namepair_registered  = DNS_name.objects.get(id = registeredID)
				namepair_registered.ip = str(namepair_registered.ip_address)
				add_service = request.POST.getlist('service_add')
				#if add_service parameter is triggered, will add the item to the model db
				if add_service:		
					for item in add_service:
						service_add = eval(item)
						values = { 	'name':service_add['dns_expr'],'dns_type':service_add['dns_type'],
								'ip_address':IPAddress(service_add['ip_address']),'description':service_add['dscr'], 'ttl': service_add['ttl']}
						AddAndLogRecord('DNS_name', DNS_name, request.user.username, values)			
				#find all other associated services and display them
				tempFilter = DNS_name.objects.filter(ip_address = ip).exclude(id = registeredID)
				regServices = list()
				for i in range(len(tempFilter)):
					[is_service_permitted, msg] = is_permitted(request, tempFilter[i].ip_address, tempFilter[i].name, tempFilter[i].dns_type)#DNS_name.objects.is_permitted(request, tempFilter[i].ip_address, tempFilter[i].name, tempFilter[i].dns_type, '', True)
					if is_service_permitted:
						tempFilter[i].ip = str(tempFilter[i].ip_address)
						regServices.append(tempFilter[i])
				#render results
				return render_to_response('qmul_dns_view_namepair.html', {'machine': namepair_registered, 'machinelists':regServices})
			else:
				form = Register_namepair_Form(initial = {'dns_expr':info['dns_expr'],'dns_type':info['dns_type'],'ip_address':info['ip_address'],'dscr':info['dscr'],'ttl': info['ttl'] })
				return render_to_response('qmul_dns_create_namepair.html',{'form':form ,'c_errors': custom_errors})
	else:
		form = Register_namepair_Form(initial = {})
	return render_to_response('qmul_dns_create_namepair.html',{'form':form })

#list all ip-name records in the model
@login_required
def dns_namepair_listing(request):
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
	#registered_pairs =  DNS_name.objects.get_permitted_records(request, True)
	registered_pairs =  DNS_name.objects.get_permitted_records(request, True, order_by, order_dir, change_dir)
	for i in range(len(registered_pairs)):#for display purposes, convert ip from integer form to str form (i.e. 3232235521 -> '192.168.0.1')
		registered_pairs[i].ip = str(registered_pairs[i].ip_address)
		registered_pairs[i].record_no = i + 1
	#get number of records per page
	try:
		list_length = int(request.GET.get('len', '400'))
	except ValueError:
		list_length = 100
	if not list_length:
		list_length = len(registered_pairs) 
	#set up pagination
	paginator = Paginator(registered_pairs, list_length, 5)
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
						mDelete.append(DeleteAndLogRecord(item, DNS_name, c_user, 'DNS_name', ''))
					mlength = len(mDelete)
					return render_to_response('qmul_dns_delete_namepair.html',{'machines':mDelete, 'mlength' : mlength})
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm(initial = {})
						return render_to_response('qmul_dns_listings_namepair.html', {'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort })
					else:
						regmachine = DNS_name.objects.get(id = item_selected[0])
						regmachine.ip = str(regmachine.ip_address)
						regServices = DNS_name.objects.filter(ip_address = regmachine.ip_address).exclude(id = regmachine.id)
						return render_to_response('qmul_dns_view_namepair.html', {'machine': regmachine, 'machinelists':regServices})
				else:
					actionForm = ViewMachinesActionForm(initial = {})
					return render_to_response('qmul_dns_listings_namepair.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort})	
			else:		
				actionForm = ViewMachinesActionForm(initial = {})
				return render_to_response('qmul_dns_listings_namepair.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort })	
	else:
		actionForm = ViewMachinesActionForm(initial = {})
		return render_to_response('qmul_dns_listings_namepair.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort})
	return render_to_response('qmul_dns_listings_namepair.html',{})

#view a single ip-name pair 
@login_required
def dns_namepair_view(request, pair_id):
	#check pair_id
	try:
		pair_id = int(pair_id)
	except ValueError:
		raise Http404()	
	#check record exists in database
	try:
		regpair = DNS_name.objects.get(id = pair_id)
	except DNS_name.DoesNotExist:
		return HttpResponseRedirect("/dns/pair/list/default")
	#check permission
	[is_valid, val] = DNS_name.objects.is_permitted(request,regpair.ip_address, regpair.name, regpair.dns_type)
	if not is_valid:
		return HttpResponseRedirect("/error/permission/")
	#get other records for viewing
	regpair.ip = str(regpair.ip_address)
	tempFilter = DNS_name.objects.filter(ip_address = regpair.ip_address).exclude(id = regpair.id)
	regServices = list()
	for i in range(len(tempFilter)):
		[is_service_permitted, msg] = DNS_name.objects.is_permitted(request,tempFilter[i].ip_address, tempFilter[i].name, tempFilter[i].dns_type)
		if is_service_permitted:
			tempFilter[i].ip = str(tempFilter[i].ip_address)
			regServices.append(tempFilter[i])
	return  render_to_response('qmul_dns_view_namepair.html', {'machine': regpair, 'machinelists': regServices})

#delete a single record 
@login_required
def dns_namepair_delete(request, pair_id):
	#check pair_id
	try:
		pair_id = int(pair_id)
	except ValueError:
		raise Http404()		
	#check record in database
	try:
		val = DNS_name.objects.get(id = pair_id)
	except DNS_name.DoesNotExist:
		return HttpResponseRedirect("/dns/pair/list/default")
	#check permission
	[is_valid, val] = DNS_name.objects.is_permitted(request,val.ip_address, val.name, val.dns_type)
	if not is_valid:
		return HttpResponseRedirect("/error/permission/")
	#delete record
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
			ip = IPAddress(info['ip_address'])
			#[can_pass, custom_errors] = dns_permission_check(request, int(IPAddress(info['ip_address'])),info['dns_expr'], info['dns_type'])
			#[is_unique, unique_error] = DNS_name.objects.is_unique(int(IPAddress(info['ip_address'])),info['dns_expr'],info['dns_type'],'',True)
			[can_pass, custom_errors] = ParameterChecks(request, ip, info['dns_expr'], info['dns_type'], pair_id, True)
			if can_pass:
				valAft = { 	'name' :info['dns_expr'],'dns_type':info['dns_type'],
						'ip_address' :ip,'description' :info['dscr'], 'ttl': info['ttl'] 	}
				modID = EditAndLogRecord('DNS_name', pair_id,  DNS_name,request.user.username, valAft)
				regpair = DNS_name.objects.get(id = modID)
				regpair.ip = str(IPAddress(regpair.ip_address))
				#regServices = DNS_name.objects.filter(ip_address = regpair.ip_address).exclude(id = modID)
				#for i in range(len(regServices)):
				#	regServices[i].ip = str(regServices[i].ip_address)
				
				tempFilter = DNS_name.objects.filter(ip_address = regpair.ip_address).exclude(id = modID)
				regServices = list()
				for i in range(len(tempFilter)):
					[is_service_permitted, msg] = is_permitted(request, tempFilter[i].ip_address, tempFilter[i].name, tempFilter[i].dns_type)#DNS_name.objects.is_permitted(request, tempFilter[i].ip_address, tempFilter[i].name, tempFilter[i].dns_type, '', True)
					if is_service_permitted:
						tempFilter[i].ip = str(tempFilter[i].ip_address)
						regServices.append(tempFilter[i])
				return render_to_response('qmul_dns_view_namepair.html', {'machine': regpair, 'machinelists':regServices})
			else:
				form = Register_namepair_Form(initial = {'dns_expr':info['dns_expr'],'dns_type':info['dns_type'],'ip_address':info['ip_address'],'dscr':info['dscr'],'ttl': info['ttl'] })
				return renderdns_fetch_records_txt_to_response('qmul_dns_edit_namepair.html',{'form':form ,'ip_id': pair_id, 'c_errors': custom_errors })
	else:
		try:
			regpair = DNS_name.objects.get(id = pair_id)		
		except DNS_name.DoesNotExist:
			return HttpResponseRedirect("/dns/pair/list/default")	
		editform = Register_namepair_Form(initial = {'dns_expr':regpair.name,'ip_address':str(regpair.ip_address),'dscr':regpair.description, 'dns_type': regpair.dns_type,'ttl': regpair.ttl })	
	return render_to_response('qmul_dns_edit_namepair.html', {'form':editform, 'ip_id': pair_id})

def dns_fetch_records_txt(request):
	registered_pairs = DNS_name.objects.all()
	for i in range(len(registered_pairs)):
		if registered_pairs[i].dns_type == '3AN':
			var = registered_pairs[i].ip_address.reverse_dns
			registered_pairs[i].ip_reverse = var.rstrip('.')
			
	return render_to_response('qmul_dns_all_data.txt', {'records':registered_pairs})
