from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from mynet.AccessControl.models import *
from mynet.HistoryLog.models import *
from django.contrib.auth.models import Group, User

import datetime, json
def get_type(value):
	if value == '1BD':
		dns_type = 'Bi-directional'	
	elif value == '2NA':
		dns_type = 'Name to address'	
	elif value == '3AN':
		dns_type = 'Address to name'
	else: 
		dns_type = ''
	return dns_type 
	
def get_model_table(val):
	if val == '1':
		model_name = DNS_names
	elif val == '2':
		model_name = DHCP_ip_pool
	elif val == '3':
		model_name = DHCP_machine
	else:
		model_name = bool(0)

	return model_name
	
def new_and_changed_keys(table_number, val_bef, val_aft):
	"""
	This function compares two python dictionaries and returns the keys (as a list)
	which are different in both dictionaries.
	If the length of the returned list is 1 and value is "EMPTYDICT", then one or both
	of the input dictionaries are empty.
	"""
	model_name = get_model_table(table_number)
	if model_name == bool(0):
		result = "EMPTYDICT"
		return result
	else:
		model_instance = model_name.objects.get(id = 1)
	if len(val_bef) == 0 or len(val_aft) == 0:
		if len(val_bef) == 0:
			val_new = val_aft
		else:
			val_new = val_bef
		result = list()	
		for (key, value) in val_new.iteritems():
			if key == 'dns_type':
				dns_type = get_type(value)	
				val = ('Type', dns_type)
			else:
				val = (model_instance._meta.get_field(key).verbose_name,value)#val = (model_instance._meta.get_field(key).verbose_name,value)
			result.append(val)
		return result
	else:
		result = list()	
		for (key, value) in val_aft.iteritems():
			try:
				if val_bef[key] != value:
					#changes = [val_bef[key], value]#str(val_bef[key] + "  to " + value)
					changes = (val_bef[key], value)
					result.append(changes)
			except KeyError:
				result.append(key)
	return result
def diff_values(table_number, val_bef, val_aft):
	"""
	This function compares two python dictionaries and returns the differences as a list in the following 
	format: [FieldName,  valueBefore , valueAfter  , is_changed]

	"""
	#get the name of the model that has been logged
	model_name = get_model_table(table_number)
	if model_name == bool(0):
		result = "EMPTYDICT"
		return result
	else:
		model_instance = model_name.objects.get(id = 1)
	result = list()	
	#check for empty values
	if len(val_aft) == 0:
		val_not_empty = val_bef
	else:
		val_not_empty = val_aft
	#go through bef and aft values and format as a list	
	for (key, value) in val_not_empty.iteritems():
		field_name  = model_instance._meta.get_field(key).verbose_name
		#check if before values are empty
		try:
			#if not val_bef[key] == '':
			before = val_bef[key]
		except KeyError:
			before = ''
		#check if after values are empty
		try:
			#if not val_aft[key] == '':
			after = val_aft[key]
		except KeyError:
			after = ''
		
		if key == 'dns_type':	#val = ['Type',(dns_type_bef, dns_type_aft),True]
			after = get_type(after)	
			before = get_type(before)			
		if before == after:			#val = [field_name,(val_bef[key],value),True]
			hasChanged = False
		elif len(val_bef) == 0 or len(val_aft) == 0:
			hasChanged = False
		else:
			hasChanged = True
			
		val = [field_name, before, after , hasChanged]
		print val
		result.append(val)
		
	return result

def LogEvent(action,val_bef, val_aft, is_bulk, uname, gname, tname):
	"""
	This function logs an event  a Record in the database and logs the event in the HistoryLog db. It returns 
	a list of the fields and values that were deleted.
		values: m_id = unique id of record in db, model_name = name of the table in db
	"""
	
	currentNetGroup = Group.objects.get(name = "Network Group")		#netgroup.objects.get(name = ngroup)
	currentUser     = User.objects.get(username__exact = uname)	#usrname.objects.get(uname = user)
	now = datetime.datetime.today()
	newEvent = log( #NetGroupName 		= currentNetGroup,
			NetUser		 	= currentUser,
			TableName		= tname,
			TimeOccured		= now,
			ActionType		= action,	
			ValuesBefore		= val_bef,
			ValuesAfter		= val_aft,
			IsBulk 			= is_bulk
		)	
	newEvent.save()
	return 

@login_required
def HistoryList(request):
	#display all key information
	historyLogs = log.objects.all() 
	
	#extract values from query dictionary and compare difference
	changed_list = list()
	log_values = log.objects.all().values() #not sure if this call if neccessary
	for i in range(len(log_values)):
		bef = eval(log_values[i]['ValuesBefore'])		#a = json.loads(log_values[i]['ValuesBefore'])
		aft = eval(log_values[i]['ValuesAfter'])		#b = json.loads(log_values[i]['ValuesAfter'])
		table_no = log_values[i]['TableName']
		changed_list.append(new_and_changed_keys(table_no,bef,aft))
	
	return render_to_response('qmul_history_listings.html', {'historyLogs':historyLogs, 'netgroupno':1, 'changed_list':changed_list})
	
@login_required
def HistoryView(request, h_id):
	try:
		h_id = int(h_id)
	except ValueError:
		raise Http404()	
	SingleLog = log.objects.get(id = h_id)
	
	#prepare before and after values for display
	ChangeLog = list()
	bef = eval(SingleLog.ValuesBefore)
	aft = eval(SingleLog.ValuesAfter)
	table_no = SingleLog.TableName
	ChangeLog.append(diff_values(table_no, bef, aft))
	#regServices = DNS_names.objects.filter(ip_pair = regpair.ip_pair).exclude(id = regpair.id)
	return render_to_response('qmul_history_view.html', {'HistoryLog':SingleLog, 'ChangeLog':ChangeLog})
	
	
