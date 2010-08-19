from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from mynet.AccessControl.models import *
from mynet.HistoryLog.models import *
from django.contrib.auth.models import Group, User

import datetime, json
def new_and_changed_keys(val_bef, val_aft):
	"""
	This function compares two python dictionaries and returns the keys (as a list)
	which are different in both dictionaries.
	If the length of the returned list is 1 and value is "EMPTYDICT", then one or both
	of the input dictionaries are empty.
	"""
	if len(val_bef) == 0 :
		result = val_aft
		return result
	elif len(val_aft) == 0:
		result = val_bef
		return result
	else:
		result = list()	
		for (key, value) in val_aft.iteritems():
			try:
				if val_bef[key] != value:
					changes = str(val_bef[key] + " :: " + value)
					result.append(changes)
			except KeyError:
				result.append(key)
	return result

def LogEvent(action,val_bef, val_aft, is_bulk, uname, gname):
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
		#a = eval(log_values[i]['ValuesBefore'])
		#b = eval(log_values[i]['ValuesAfter'])
		a = json.loads(log_values[i]['ValuesBefore'])
		b = json.loads(log_values[i]['ValuesAfter'])
		changed_list.append(new_and_changed_keys(a,b))
	
	return render_to_response('qmul_history.html', {'historyLogs':historyLogs, 'netgroupno':1, 'changed_list':changed_list})
	
	
	
