from django.shortcuts import render_to_response
from django.template import RequestContext
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
import datetime, json

#################################################################################
####################### DNS NAME Pair ###########################################
#################################################################################
def prepare_values(action, vals, uname, m_id):
	'''
	Prepares the values, so as to be returned to the funtion AddAndLogRecord or EditAndLogRecord
	Arguments:
		action - 'A' Adding, or 'E' editing
		vals - values to add to the database
		uname - django username objects
		m_id - if editing, specified the id of the record to be modified
	'''
	is_bulk = False
	now = datetime.datetime.today()
	table_number = '1' #for logging purposes
	values = { 'name':vals['dns_expr'],'dns_type':vals['dns_type'],
		'ip_address':IPAddress(vals['ip_address']),'description':vals['dscr'],'ttl': vals['ttl'] }
	try:
		values['ttl'] = int(values['ttl'])
	except:
		values['ttl'] = 0
		
	if action == 'A':
		if values['ip_address'].version == 6:
			ipVersion = True
		else:
			ipVersion = False
		tp = values['dns_type']
		if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
			tp = '1BD'
		Record = DNS_name( 		name = values['name'], 	ip_address = values['ip_address'],
								dns_type = tp, 			is_ipv6 = ipVersion,
								time_created = now,		time_modified = now,
								ttl = values['ttl'], 	description = values['description']							
					)
		preparedValues = Record, uname, table_number, is_bulk
	elif action == 'E':
		is_modified = bool(0)
		try :
			ModifiedRecord = DNS_name.objects.get(id = m_id)
		except model_name.DoesNotExist:
			return False
		valuesBefore = ModifiedRecord.LogRepresentation()
		if not ModifiedRecord.name == values['name']: 
			ModifiedRecord.name = values['name']
			is_modified = bool(1)
		if not ModifiedRecord.ttl == values['ttl']: 
			ModifiedRecord.ttl = values['ttl']
			is_modified = bool(1)
		if not ModifiedRecord.description == values['description']:
			if CompareDescriptions(ModifiedRecord.description, values['description']):
				ModifiedRecord.description = values['description']
				is_modified = bool(1)	
		if not ModifiedRecord.dns_type == values['dns_type']:
			tp = values['dns_type']
			if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
				tp = '1BD'
			ModifiedRecord.dns_type = values['dns_type']
			is_modified = bool(1)
		if not ModifiedRecord.ip_address == values['ip_address']:
			ModifiedRecord.ip_address = values['ip_address']
			is_modified = bool(1)
			if (values['ip_address'].version == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			ModifiedRecord.is_ipv6 = ipVersion	
		if not ModifiedRecord.ttl == values['ttl']:
			ModifiedRecord.ttl = values['ttl']
			is_modified = bool(1)
		preparedValues = ModifiedRecord, uname, table_number, is_modified, valuesBefore, str(values), is_bulk
	else:
		pass
	return preparedValues
def ParameterChecks(user_object, ip, name, dt, rid, enable_softcheck):
	"""
	This function calls is_unique and is_permitted dns test and consolidates errors. Returns True if there are no errors
	and return False otherwise. If there are errors, error_msg will contain a message relating to the nature of the error
	Arguments:
		user_object		= request object
		ip				= ip address (in netaddr IPAddress object) 
		name			= machine name
		dt				= dns type
		rid				= if present, the id of the record, usually an integer
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
	'''
	Handle the additional page that is opened when the user clicks on 'ADD Service'
	'''
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
				#[canpass, custom_errors] = dns_permission_check(request, int(IPAddress(original_machine.ip_address)), newObject['service_name'], "2NA")
				[can_pass, custom_errors] = ParameterChecks(request, IPAddress(original_machine.ip_address), newObject['service_name'], "2NA",  original_id, True)
				if can_pass:
					newObject['dns_type'] = '2NA'
					newObject['ip_address'] = original_machine.ip_address
					newObject['dns_expr'] = newObject['service_name']
					print newObject
					AddAndLogRecord(prepare_values('A', newObject, request.user, ''))
					display = "Added " + " " + newObject['service_name']
					return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script> <p>Test to display.</p>' %\
						(newObject, display )) #._get_pk_val()
				else:
					pageContext = {'form': form, 'field': field, 'mach':mn_pair, 'ip':str(ip_address),'c_errors': custom_errors}
					return render_to_response("qmul_dns_create_simple.html", pageContext , context_instance=RequestContext(request))
			else:
				response = render_to_response('qmul_dns_create_simple.html',{'form':form }, context_instance=RequestContext(request))
	else:		
		form = addForm()#initial = {})
	pageContext = {'form': form, 'field': field, 'mach':mn_pair, 'ip':str(ip_address) }
	return render_to_response("qmul_dns_create_simple.html", pageContext, context_instance=RequestContext(request))

#Add an IP-name pair to modelquery set
@login_required
def dns_namepair_add(request):
	'''
	This function adds a dns record to the DNS_name table in the database. Validation is done through ParameterChecks#
	function.
	'''
	if request.method == 'POST':
		form = Register_namepair_Form(request.POST)
		if form.is_valid():
			info = form.cleaned_data
			ip = IPAddress(info['ip_address'])
			[can_pass, custom_errors] = ParameterChecks(request, ip, info['dns_expr'], info['dns_type'], '', True)
			#check if this form is permitted first
			if can_pass:
				registeredID = AddAndLogRecord(prepare_values('A', info, request.user, ''))
				namepair_registered  = DNS_name.objects.get(id = registeredID)
				namepair_registered.ip = str(namepair_registered.ip_address)
				add_service = request.POST.getlist('service_add')
				#if add_service parameter is triggered, will add the item to the model db
				if add_service:		
					for item in add_service:
						service_add = eval(item)
						AddAndLogRecord(prepare_values('A', service_add, request.user, ''))
				#find all other associated services and display them
				tempFilter = DNS_name.objects.filter(ip_address = ip).exclude(id = registeredID)
				regServices = list()
				for item in tempFilter:
					[is_service_permitted, msg] = DNS_name.objects.is_permitted(request, item.ip_address, item.name, item.dns_type)
					if is_service_permitted:
						regServices.append(item)
				#redirect results
				url = "/dns/pair/%s/view" % registeredID
				response = HttpResponseRedirect(url)
			else:
				response = render_to_response('qmul_dns_create_namepair.html',{'form':form ,'c_errors': custom_errors}, context_instance=RequestContext(request))
		else:
			response = render_to_response('qmul_dns_create_namepair.html',{'form':form }, context_instance=RequestContext(request))
	else:
		form = Register_namepair_Form()#initial = {})
		response = render_to_response('qmul_dns_create_namepair.html',{'form':form }, context_instance=RequestContext(request))
	return response

#list all ip-name records in the model
@login_required
def dns_namepair_listing(request):
	'''
	This view function is responsible for displaying a list of all the permitted records a user is allowed to
	control. It also handles the pagination, order by, and order directions. 
	'''
	import time
	time_started = time.time()
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
	time_t1 = time.time()
	registered_pairs =  DNS_name.objects.get_permitted_records(request, True, order_by, order_dir, change_dir)
	time_t2 = time.time()
	time_t3 = time.time()
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
					for item in item_selected:
						mDelete.append(DeleteAndLogRecord(item, DNS_name, request.user, 'DNS_name', ''))
					mlength = len(mDelete)
					time_middle = time.time()
					response = render_to_response('qmul_dns_delete_namepair.html',{'machines':mDelete, 'mlength' : mlength}, context_instance=RequestContext(request))
				elif action == 'vue':
					if len(item_selected) > 1:
						actionForm = ViewMachinesActionForm()#initial = {})
						time_middle = time.time()
						response = render_to_response('qmul_dns_listings_namepair.html', {'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort }, context_instance=RequestContext(request))
					else:
						regmachine = DNS_name.objects.get(id = item_selected[0])
						regmachine.ip = str(regmachine.ip_address)
						regServices = DNS_name.objects.filter(ip_address = regmachine.ip_address).exclude(id = regmachine.id)
						time_middle = time.time()
						response = render_to_response('qmul_dns_view_namepair.html', {'machine': regmachine, 'machinelists':regServices}, context_instance=RequestContext(request))
				else:
					actionForm = ViewMachinesActionForm()#initial = {})
					time_middle = time.time()
					response = render_to_response('qmul_dns_listings_namepair.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort}, context_instance=RequestContext(request))	
			else:		
				actionForm = ViewMachinesActionForm()#initial = {})
				time_middle = time.time()
				response = render_to_response('qmul_dns_listings_namepair.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort }, context_instance=RequestContext(request))	
	else:
		actionForm = ViewMachinesActionForm()#initial = {})
		time_middle = time.time()
		response = render_to_response('qmul_dns_listings_namepair.html',{'form':actionForm, 'machinelists' : page, 'list_size':list_length, 'sort':sort}, context_instance=RequestContext(request))
	#response = render_to_response('qmul_dns_listings_namepair.html',{})
	time_stopped = time.time()
	request.session["_dns_list_total_timing"] = str(time_stopped - time_started)
	request.session["_dns_list_view_timing"] = str(time_middle - time_started)
	request.session["_dns_list_template_timing"] = str(time_stopped - time_middle)
	request.session["_dns_list_t1t2_timing"] = str(time_t2 - time_t1)
	request.session["_dns_list_t2t3_timing"] = str(time_t3 - time_t2)
	print 'Total time:',str(time_stopped - time_started)
	print 'view time:',str(time_middle - time_started)
	print 'template time',str(time_stopped - time_middle)
	print 'time between t2 and t1:', time_t2 - time_t1
	print 'time between t3 and t2:', time_t3 - time_t2
	return response
#view a single ip-name pair 
@login_required
def dns_namepair_view(request, pair_id):
	'''
	This function finds the record with the id = pair_id and prepare the record for displaying. Function also checks
	that the user is permitted to view this record and well as checking if the record exists in the database.
	'''
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
	for item in tempFilter:
		[is_service_permitted, msg] = DNS_name.objects.is_permitted(request,item.ip_address, item.name, item.dns_type)
		if is_service_permitted:
			regServices.append(item)
	return  render_to_response('qmul_dns_view_namepair.html', {'machine': regpair, 'machinelists': regServices}, context_instance=RequestContext(request))

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
	mDelete.append(DeleteAndLogRecord(pair_id, DNS_name, request.user, 'DNS_name', ''))
	mlength = len(mDelete) 
	return render_to_response('qmul_dns_delete_namepair.html',{'machines':mDelete, 'mlength':mlength}, context_instance=RequestContext(request))
	
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
			[can_pass, custom_errors] = ParameterChecks(request, ip, info['dns_expr'], info['dns_type'], pair_id, True)
			if can_pass:
				modID = EditAndLogRecord(prepare_values('E', info, request.user, pair_id))
				regpair = DNS_name.objects.get(id = modID)				
				tempFilter = DNS_name.objects.filter(ip_address = regpair.ip_address).exclude(id = modID)
				regServices = list()
				for item in tempFilter:
					[is_service_permitted, msg] = DNS_name.objects.is_permitted(request, item.ip_address, item.name, item.dns_type)
					if is_service_permitted:
						regServices.append(item)
				url = "/dns/pair/%s/view" % modID
				response = HttpResponseRedirect(url)
			else:
				response = render_to_response('qmul_dns_edit_namepair.html',{'form':editform ,'ip_id': pair_id, 'c_errors': custom_errors }, context_instance=RequestContext(request))
		else:
			response = render_to_response('qmul_dns_edit_namepair.html',{'form':editform }, context_instance=RequestContext(request))
	else:
		try:
			regpair = DNS_name.objects.get(id = pair_id)		
			editform = Register_namepair_Form(initial = {'dns_expr':regpair.name,'ip_address':str(regpair.ip_address),'dscr':regpair.description, 'dns_type': regpair.dns_type,'ttl': regpair.ttl })	
			response = render_to_response('qmul_dns_edit_namepair.html', {'form':editform, 'ip_id': pair_id}, context_instance=RequestContext(request))
		except DNS_name.DoesNotExist:
			response = HttpResponseRedirect("/dns/pair/list/default")	
	return response
def dns_fetch_records_txt(request):
	'''
	Responsible for displaying all dns records in tinydns format (plain/text)
	'''
	registered_pairs = DNS_name.objects.all()
	data_format = request.GET.get('format', 'txt')
	if data_format == 'txt' or data_format == 'djb':
		for registered_pair in registered_pairs:
			if registered_pair.ttl == 0 or type(registered_pair.ttl) == type(None):
				registered_pair.ttl = 86400 #default value
			if registered_pair.dns_type == '3AN':
				registered_pair.ip_reverse = registered_pair.ip_address.reverse_dns.rstrip('.')
			if registered_pair.is_ipv6:
				registered_pair.ip_address_v6 = hex(registered_pair.ip_address).lstrip('0x')
		response = render_to_response('qmul_dns_all_data.txt', {'records':registered_pairs}, mimetype = 'text/plain')
	elif data_format == 'json':
		data = []
		if not registered_pairs:
			data = ['#None']
		else:
			for registered_pair in registered_pairs:
				if registered_pair.ttl == 0 or type(registered_pair.ttl) == type(None):
					ttl = 86400 #default value
				else:
					ttl = registered_pair.ttl
				data.append({'name':registered_pair.name, 'ip_address':str(registered_pair.ip_address),
							'ttl': ttl, 'description':registered_pair.description,
							'dns_type':registered_pair.dns_type})
		response = HttpResponse(json.dumps(data, indent=2), mimetype='application/json')
	else:
		error = 'Unknown format type - %s' %data_format
		response = render_to_response('qmul_dns_all_data.txt', {'error':error}, mimetype = 'text/plain')
	return response
	
