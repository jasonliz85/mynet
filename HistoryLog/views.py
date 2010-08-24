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
		dns_type = bool(false)
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
def history(request):
	#display all key information
	historyLogs = log.objects.all() 
	
	#extract values from query dictionary and compare difference
	changed_list = list()
	log_values = log.objects.all().values()
	for i in range(len(log_values)):
		bef = eval(log_values[i]['ValuesBefore'])		#a = json.loads(log_values[i]['ValuesBefore'])
		aft = eval(log_values[i]['ValuesAfter'])		#b = json.loads(log_values[i]['ValuesAfter'])
		table_no = log_values[i]['TableName']
		changed_list.append(new_and_changed_keys(table_no,bef,aft))
	
	return render_to_response('qmul_history.html', {'historyLogs':historyLogs, 'netgroupno':1, 'changed_list':changed_list})
	
	
	
