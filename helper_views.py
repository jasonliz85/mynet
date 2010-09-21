from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

from mynet.HistoryLog.models import *
from mynet.DHCP.models import *
from mynet.DNS.models import *
from mynet.HistoryLog.views import *

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

def EditAndLogRecord(m_name_str, m_id, model_name, uname, values): 
	"""
	This function edits a Record in the database and logs the event in the HistoryLog db
		arguments: m_id = unique id of record in db, model_name = name of the table in db
	"""
	#initialize values
	is_modified = bool(0)
	try :
		mod_record = model_name.objects.get(id = m_id)
	except model_name.DoesNotExist:
		return False
		
	valBef = mod_record.LogRepresentation()
	t_number = get_table_number(m_name_str)
	#switch to appropriete model and deal with each slightly differently
	if m_name_str == "DNS_name":	
		if not mod_record.name == values['name']: 
			mod_record.name = values['name']
			is_modified = bool(1)
		if not mod_record.description == values['description']:
			if CompareDescriptions(mod_record.description, values['description']):
				mod_record.description = values['description']
				is_modified = bool(1)	
		if not mod_record.dns_type == values['dns_type']:
			tp = values['dns_type']
			if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
				tp = '1BD'
			mod_record.dns_type = values['dns_type']
			is_modified = bool(1)
		if not mod_record.ip_address == values['ip_address']:
			mod_record.ip_address = values['ip_address']
			is_modified = bool(1)
			if (values['ip_address'].version == 6):
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			mod_record.is_ipv6 = ipVersion		
	elif m_name_str == "DHCP_ip_pool":
		if not mod_record.ip_first == values['ip_first']:
			if values['ip_first'].version == 6:
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			is_modified = bool(1)
			mod_record.ip_first = values['ip_first']
			mod_record.is_ipv6 = ipVersion
		if not mod_record.ip_last == values['ip_last']:
			mod_record.ip_last = values['ip_last']
			is_modified = bool(1)
		if not mod_record.description == values['description']:
			if CompareDescriptions(mod_record.description, values['description']):
				mod_record.description = values['description']
				is_modified = bool(1)
	elif m_name_str == "DHCP_machine":
		if not mod_record.mac_address == str(EUI(values['mac_address'], dialect=mac_custom)):
			mod_record.mac_address = str(EUI(values['mac_address'], dialect=mac_custom))
			is_modified = bool(1)
		if not mod_record.ip_address == values['ip_address']:
			mod_record.ip_address = values['ip_address']
			if values['ip_address'].version == 6:
				ipVersion = bool(1)
			else:
				ipVersion = bool(0)
			mod_record.is_ipv6 = ipVersion
			is_modified = bool(1)
		if not mod_record.host_name == values['host_name']:
			mod_record.host_name = values['host_name']
			is_modified = bool(1)
		if not mod_record.description == values['description']:
			if CompareDescriptions(mod_record.description, values['description']):
				mod_record.description = values['description']
				is_modified = bool(1)
	else: 
		return bool(0)
		
	if is_modified:		
		now = datetime.datetime.today()
		final_values = str(values)
		init_values = str(valBef)
		mod_record.time_modified = now
		mod_record.save()
		LogEvent('E',init_values, final_values, False, uname, "NetGroup:ToDo", t_number, m_id)
		
	return mod_record.id
	
def AddAndLogRecord(m_name_str, model_name, uname, values):
	"""
	This function adds a Record in the database and logs the event in the HistoryLog db.
	"""
	now = datetime.datetime.today()
	t_number = get_table_number(m_name_str)
	#check ip address if version 6
	try: 
		if (IPAddress(values['ip_address']).version == 6):
			ipVersion = True
		else:
			ipVersion = False
	except KeyError:
		pass
	
	if m_name_str == "DNS_name":
		tp = values['dns_typ']
		if not (tp == '1BD' or tp == '2NA' or tp == '3AN'):
			tp = '1BD'
		newRecord = model_name( name	= values['name'],
					ip_address	= values['ip_address'],
					dns_type	= tp,
					is_ipv6 	= ipVersion,
					time_created 	= now,
					time_modified	= now,
					description 	= values['description']								
					)
	elif m_name_str == "DHCP_ip_pool":		
		if (IPAddress(values['ip_first']).version == 6):
			ipVersion = bool(1)
		else:
			ipVersion = bool(0)				
		newRecord = model_name(	ip_first	= values['ip_first'],
					ip_last		= values['ip_last'],
					is_ipv6 	= ipVersion,
					time_created 	= now,					
					time_modified	= now,
					description 	= values['description']								
					)
	elif m_name_str == "DHCP_machine":
		newRecord = model_name(	mac_address 	= str(EUI(values['mac_address'], dialect=mac_custom)),
					ip_address  	= values['ip_address'],
					host_name  	= values['host_name'],
					is_ipv6  	= ipVersion,
					time_created 	= now,
					time_modified	= now,
					description 	= values['description']
					)
	else: 
		return bool(0)
	newRecord.save() #vals = model_name.objects.filter(id = newRecord.id).values() 
	init_values = "{}" 
	final_values = newRecord.LogRepresentation()#str(vals[0])
	print final_values
	LogEvent('A',init_values, final_values, False, uname, "NetGroup:ToDo", t_number, newRecord.id)
	return newRecord.id
		
def DeleteAndLogRecord(m_id, Model_Name, uname, table_name, action):
	"""
	This function deletes a Re0cord in the database and logs the event in the HistoryLog db. It returns 
	a list of the fields and values that were deleted.
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
	if len(action) == 0:
		action = 'D'
	#log event 
	LogEvent(action,init_values, final_values, False, uname, "NetGroup:ToDo", t_number, m_id)

	return DeleteRecord
	
