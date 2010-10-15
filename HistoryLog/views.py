from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.models import Group, User

from subnets.AccessControl.models import *
from subnets.HistoryLog.models import *
from subnets.AccessControl.views import *
from subnets.helper_views import *

import datetime

def UndoLogAction(SingleLog, username):
	'''
	Not Completed!
	'''
	record_id = SingleLog.RecordID
	table_name = get_table_name(SingleLog.TableName)
	model_name = get_model_table(SingleLog.TableName)
	Action_type = SingleLog.ActionType
	Value_bef = SingleLog.ValuesBefore
	Value_aft = SingleLog.ValuesAfter
	
	if Action_type == 'D':
		pass
	elif Action_type == 'A':
		DeleteAndLogRecord(record_id, model_name, username, table_name, 'U')
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
		model_instance = model_name.objects.all()[0] #get the first record in database
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
					if key == 'dns_type':
						after = get_dns_type(val_bef[key])	
						before = get_dns_type(value)	
						changes = (before, after)
					else:
						changes = (val_bef[key], value)
					result.append(changes)
			except KeyError:
				result.append(key)
	return result
def MulitpleViewFormat(table_number, val_bef, val_aft):
	"""
	This function compares two python dictionaries and returns the differences as a list of twos strings in the following 
	format: [Before Values, After Values]
	Before Values: "IP Address: a1.b1.c1.d1 \n MAC Address: aa.bb.cc.dd.ee.ff \n ...etc"
	After Values:  "IP Address: a2.b2.c2.d2 \n MAC Address: aa.bb.cc.dd.ee.ff \n ...etc
	"""
	#get the name of the model that has been logged
	model_name = get_model_table(table_number)
	if model_name == bool(0):
		result = "EMPTYDICT"
		return result
	else:
		model_instance = model_name.objects.all()[0]
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
			hasChanged = ''
		elif len(val_bef) == 0:
			hasChanged = '+'
		elif len(val_aft) == 0:
			after = before 
			hasChanged = '-'
		else:
			hasChanged = '*'
		#The List that is returned			
		val = hasChanged + str(field_name) + " : "  + str(after) + "\n"
		result.append(val)
		
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
		model_instance = model_name.objects.all()[0] 
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
		#check if after values acleaning my house ukre empty
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

@login_required
def HistoryList(request):
	#display all key informationcleaning my house uk
	if request.user.is_staff:
		#get order direction, and order type
		order_dir = request.GET.get('ot', 'desc')
		order_by = request.GET.get('o', 'time')
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
		historyLogs = log.objects.all() 
		#get number of records per page
		try:
			list_length = int(request.GET.get('len', '400'))
		except ValueError:
			list_length = 100
		if not list_length:
			list_length = len(historyLogs) 
		#set up pagination
		paginator = Paginator(historyLogs, list_length, 5)
		try:
			page = paginator.page(page_index)
		except (EmptyPage, InvalidPage), e:
			page = paginator.page(paginator.num_pages)
		#get post details
		#extract values from query dictionary and compare difference
		changed_list = list()
		log_values = log.objects.all().values() #not sure if this call if neccessary
		for i in range(len(log_values)):
			bef = eval(log_values[i]['ValuesBefore'])		#a = json.loads(log_values[i]['ValuesBefore'])
			aft = eval(log_values[i]['ValuesAfter'])		#b = json.loads(log_values[i]['ValuesAfter'])
			table_no = log_values[i]['TableName']
			changed_list.append(NewAndChangedKeys(table_no,bef,aft))
		
		return render_to_response('qmul_history_listings.html', {'historyLogs':page, 'netgroupno':1, 'changed_list':changed_list, 'list_size':list_length, 'sort':sort })
	else:
		return render_to_response('qmul_history_listings.html', {'historyLogs':'', 'PermissionError': True})
		
@login_required
def HistoryView(request, h_id):
	if request.user.is_staff:
		try:
			h_id = int(h_id)
		except ValueError:
			raise Http404()	
		try:
			SingleLog = log.objects.get(id = h_id)
		except log.DoesNotExist:
			return HttpResponseRedirect("/history")
	
		#prepare before and after values for display
		ChangeLog = list()
		bef = eval(SingleLog.ValuesBefore)
		aft = eval(SingleLog.ValuesAfter)
		table_no = SingleLog.TableName
		ChangeLog.append(diff_values(table_no, bef, aft))
		#regServices = DNS_name.objects.filter(ip_pair = regpair.ip_pair).exclude(id = regpair.id)
		return render_to_response( 'qmul_history_view.html' , {'HistoryLog':SingleLog, 'ChangeLog':ChangeLog})
	else:
		return render_to_response('qmul_history_view.html', {'HistoryLog':'', 'PermissionError': True})
		
def HistoryView2(request, h_id):
	if request.user.is_staff:
		try:
			h_id = int(h_id)
		except ValueError:
			raise Http404()	
		try:
			SingleLog = log.objects.get(id = h_id)
		except log.DoesNotExist:
			return HttpResponseRedirect("/history")
		
		Logs = log.objects.filter(TableName = SingleLog.TableName, RecordID = SingleLog.RecordID)
		ChangeLog = list()
		for i in range(len(Logs)):
			bef = eval(Logs[i].ValuesBefore)
			aft = eval(Logs[i].ValuesAfter)
			table_no = Logs[i].TableName
			ChangeLog.append(MulitpleViewFormat(table_no, bef, aft))
		return render_to_response( 'qmul_history_view_multiple.html' , {'HistoryLogs':Logs, 'ChangeLog':ChangeLog})
	else:
		return render_to_response('qmul_history_view_multiple.html', {'HistoryLog':'', 'PermissionError': True})
@login_required
def HistoryUndoAction(request, h_id):
	try:
		h_id = int(h_id)
	except ValueError:
		raise Http404()
	historyRecords = list()
	try:
		SingleLog = log.objects.get(id = h_id)
	except log.DoesNotExist:
		return HttpResponseRedirect("/history")
		
	historyRecords.append(SingleLog)
	
	val = historyRecords[0]
	if UndoLogAction(val, request.user.username):
		Message = 'This log was succesfully restored.'
	else:
		Message = 'There was a problem restoring this action.'
	
	hlength = len(historyRecords)
	
	return render_to_response('qmul_history_undo.html', {'historyRecords':historyRecords, 'Message':Message, 'hlength':hlength}) 
	
