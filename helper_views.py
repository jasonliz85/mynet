from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from subnets.HistoryLog.models import *
from subnets.DHCP.models import *
from subnets.DNS.models import *
from subnets.HistoryLog.views import *

from netaddr import *
import datetime, difflib

class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'

def get_dns_type(value):
	'''
	Returns the dns type in string
	'''
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
	'''
	Returns the model object given the input number
	'''
	if val == '1':
		model_name = DNS_name
	elif val == '2':
		model_name = DHCP_ip_pool
	elif val == '3':
		model_name = DHCP_machine
	else:
		model_name = False
		print 'Error: get_model_table(), table number not valid'		
	return model_name
	
def get_table_name(val):
	'''
	Returns the table name in string given the input number
	'''
	if val == '1':
		table_name = 'DNS_name'
	elif val == '2':
		table_name = 'DHCP_ip_pool'
	elif val == '3':
		table_name = 'DHCP_machine'
	else:
		table_name = False
		print 'Error: get_table_name(), table number not valid'		
	return table_name
	
def get_table_number(table_name):
	'''
	Returns the table number given the string table name
	'''
	if table_name == 'DNS_name':
		table_number = '1'
	elif table_name == 'DHCP_ip_pool':
		table_number = '2'
	elif table_name ==  'DHCP_machine':	
		table_number = '3'
	else:
		print 'Error: get_table_number(), table name not recognised'
		table_number = False		
	return table_number
	
def LogEvent(action,val_bef, val_aft, is_bulk, uname, nr_ip_subnets, nr_dns_expressions, tname, tid):
	"""
	This function logs an event  a Record in the database and logs the event in the HistoryLog db. It returns 
	a list of the fields and values that were deleted.
		values: m_id = unique id of record in db, model_name = name of the table in db
	"""	
	#currentNetGroup = Group.objects.get(name = "Network Group")		#netgroup.objects.get(name = ngroup)
	#print currentNetGroup
	currentUser     = uname #User.objects.get(username__exact = uname)	#usrname.objects.get(uname = user)
	now = datetime.datetime.today()
	newEvent = log( NetUser		 	= currentUser,
					TableName		= tname,
					RecordID		= tid,
					TimeOccured		= now,
					ActionType		= action,	
					ValuesBefore	= val_bef,
					ValuesAfter		= val_aft,
					IsBulk 			= is_bulk
		)	
	newEvent.save()
	for subnet in nr_ip_subnets:
		newEvent.NetResource_ipsubnets.add(subnet)
	for expression in nr_dns_expressions:
		newEvent.NetResource_dnsexpressions.add(expression)
	newEvent.save()
	return 
	
def CompareDescriptions(dsrc1, dsrc2):
	"""
	This function compares two strings and determines whether the difference between the two is a white space
	"""
	changed = bool(0)
	s = difflib.SequenceMatcher(None, dsrc1, dsrc2)
	for tag, i1, i2, j1, j2 in s.get_opcodes():
 		if tag == 'insert':
 			if dsrc1[i1:i2] == '' and dsrc2[j1:j2] == ' ' or dsrc1[i1:i2] == ' ' and dsrc2[j1:j2] == '':
 				changed = bool(0)
 			else:
 				changed = bool(1)
 		elif tag == 'replace':
 			if dsrc1[i1:i2] == '' and dsrc2[j1:j2] == ' ' or dsrc1[i1:i2] == ' ' and dsrc2[j1:j2] == '':
 				changed = bool(0)
 			else:
 				changed = bool(1)
 		elif tag == 'delete':
 			if dsrc1[i1:i2] == '' and dsrc2[j1:j2] == ' ' or dsrc1[i1:i2] == ' ' and dsrc2[j1:j2] == '':
 				changed = bool(0)
 			else:
 				changed = bool(1)
	return changed

def EditAndLogRecord(var):
	"""
	This function edits a Record in the database and logs the event in the HistoryLog db. Assumes the input 'var'
	contains a list of three objects: var[0] - django model object, var[1] - django username object,
	var[2] - table number (1 = DNS_names, 2 = , 3 = ), var[3] - is modified, var[4] - values before changes, var[5] - values after change
	"""
	values = {'mod_record': var[0], 'uname': var[1], 't_number': var[2], 'is_modified': var[3], 'valuesBefore':var[4], 'valuesAfter':var[5]}
	if values['is_modified']:		
		now = datetime.datetime.today()
		values['mod_record'].time_modified = now
		values['mod_record'].save()
		net_res_ip_subnets = get_address_blocks_managed_by(values['uname'])
		net_res_ip_express = get_dns_patterns_managed_by(values['uname'])
		try:
			is_bulk = var[6]
		except IndexError:
			is_bulk = False
		LogEvent('E', values['valuesBefore'], values['valuesAfter'], is_bulk, values['uname'], net_res_ip_subnets, net_res_ip_express, values['t_number'], values['mod_record'].id)
	return values['mod_record'].id
def AddAndLogRecord(var):
	"""
	This function adds a Record in the database and logs the event in the HistoryLog db. Assumes the input 'var'
	contains a list of three objects: var[0] - django model object, var[1] - django username object, var[2] - table number (1 = DNS_names, 2 = , 3 = )
	"""
	values = {'newRecord': var[0], 'uname': var[1], 't_number': var[2]}
	init_values = "{}" 
	final_values = values['newRecord'].LogRepresentation() #LogRepresentation should be defined in the model definitions model.py
	#Save and LOG results
	values['newRecord'].save() 
	net_res_ip_subnets = get_address_blocks_managed_by(values['uname'])
	net_res_ip_express = get_dns_patterns_managed_by(values['uname'])
	try:
		is_bulk = var[3]
	except IndexError:
		is_bulk = False
	LogEvent('A',init_values, final_values, is_bulk, values['uname'], net_res_ip_subnets, net_res_ip_express, values['t_number'], values['newRecord'].id)

	return values['newRecord'].id

def DeleteAndLogRecord(m_id, Model_Name, uname, table_name, action):
	"""
	This function deletes a Re0cord in the database and logs the event in the HistoryLog db. It returns 
	a list test1.students.qmul.ac.ukof the fields and values that were deleted.
		values: m_id = unique id of record in db, model_name = name of the table in db, uname =
	"""
	t_number = get_table_number(table_name)
	try :
		DeleteRecord = Model_Name.objects.get(id = m_id)
	except Model_Name.DoesNotExist:
		return False
	
	init_values = DeleteRecord.LogRepresentation() 	#init_values = str(vals[0]) 	#json.dumps(vals[0], sort_keys=True, indent=0) 	
	final_values = "{}"				#json.dumps("{}", sort_keys=True, indent=0)   returnRecordList.append(DeleteRecord)
	DeleteRecord.delete()
	net_res_ip_subnets = get_address_blocks_managed_by(uname)
	net_res_ip_express = get_dns_patterns_managed_by(uname)
	if len(action) == 0:
		action = 'D'
	#log event 
	LogEvent(action,init_values, final_values, False, uname, net_res_ip_subnets, net_res_ip_express, t_number, m_id)

	return DeleteRecord
	
