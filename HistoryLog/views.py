from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from mynet.AccessControl.models import *
from mynet.HistoryLog.models import *
from mynet.AccessControl.views import *
from django.contrib.auth.models import Group, User

import datetime, json

def get_dns_type(value):
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
		model_name = False
		print 'Error: get_model_table(), table number not valid'
		
	return model_name
def get_table_name(val):
	if val == '1':
		table_name = 'DNS_names'
	elif val == '2':
		table_name = 'DHCP_ip_pool'
	elif val == '3':
		table_name = 'DHCP_machine'
	else:
		table_name = False
		print 'Error: get_table_name(), table number not valid'
		
	return table_name
def get_table_number(table_name):
	if table_name == 'DNS_names':
		table_number = '1'
	elif table_name == 'DHCP_ip_pool':
		table_number = '2'
	elif table_name ==  'DHCP_machine':	
		table_number = '3'
	else:
		print 'Error: get_table_number(), table name not recognised'
		table_number = False
		
	return table_number
def UndoLogAction(SingleLog, username):
	
	record_id = SingleLog.RecordID
	table_name = get_table_name(SingleLog.TableName)
	model_name = get_model_table(SingleLog.TableName)
	Action_type = SingleLog.ActionType
	Value_bef = SingleLog.ValuesBefore
	Value_aft = SingleLog.ValuesAfter
	
	if Action_type == 'D':
		pass
	elif Action_type == 'A':
		DeleteAndLogRecord(record_id, model_name, username, table_name)
	elif Action_type == 'M':
		pass
	elif Action_type == 'U':
		pass
	elif Action_type == 'R':
		pass
	
	return True
def NewAndChangedKeys(table_number, val_bef, val_aft):
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
				dns_type = get_dns_type(value)	
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
			before = val_bef[key]
		except KeyError:
			before = ''
		#check if after values are empty
		try:
			after = val_aft[key]
		except KeyError:
			after = ''
		#if dns_type, change the format slightly
		if key == 'dns_type':	
			after = get_dns_type(after)	
			before = get_dns_type(before)	
		#check the before and after fields to see if they have changed (for highlighting purposes)		
		if before == after:					
			hasChanged = False
		elif len(val_bef) == 0 or len(val_aft) == 0:
			hasChanged = False
		else:
			hasChanged = True
		#The List that is returned	
		val = [field_name, before, after , hasChanged]
		result.append(val)
		
	return result

def LogEvent(action,val_bef, val_aft, is_bulk, uname, gname, tname, tid):
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
			RecordID		= tid,
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
		changed_list.append(NewAndChangedKeys(table_no,bef,aft))
	
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

@login_required
def HistoryUndoAction(request, h_id):
	try:
		h_id = int(h_id)
	except ValueError:
		raise Http404()
	historyRecords = list()
	historyRecords.append(log.objects.get(id = h_id))
	val = historyRecords[0]
	if UndoLogAction(val, request.user.username):
		Message = 'This log was succesfully restored.'
	else:
		Message = 'There was a problem restoring this action.'
	
	hlength = len(historyRecords)
	return render_to_response('qmul_history_undo.html', {'historyRecords':historyRecords, 'Message':Message, 'hlength':hlength}) 
	
