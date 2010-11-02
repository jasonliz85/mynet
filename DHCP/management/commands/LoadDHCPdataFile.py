from django.core.management.base import LabelCommand
from netaddr import *
import datetime
from subnets.DHCP.models import *
from subnets.helper_views import AddAndLogRecord
from django.contrib.auth.models import User
class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'

def prepare_values(action, table_type, values, uname, m_id):
	'''
	Prepares the values, so as to be returned to the funtion AddAndLogRecord or EditAndLogRecord
	Arguments:
		action - 'A' Adding, or 'E' editing
		table_type - 'pool' or 'machine'
		vals - values to add to the database
		uname - django username objects
		m_id - if editing, specified the id of the record to be modified
	'''
	now = datetime.datetime.today()
	#initialising common values used for both 'E' and 
	if table_type == 'pool':
		#values = {'ip_first':IPAddress(vals['ip_first']), 'ip_last':IPAddress(vals['ip_last']),'description':vals['description'] }
		table_number = '2'
		if values['ip_first'].version == 6 and values['ip_last'].version == 6:
			ipVersion = True
		else:
			ipVersion = False
	elif table_type == 'machine':
		#values = {'mac_address' :str(EUI(vals['mac_address'], dialect=mac_custom)),'ip_address': IPAddress(vals['ip_address']),'host_name':vals['host_name'],'description':vals['description'] }
		table_number = '3'
		if values['ip_address'].version == 6:
			ipVersion = True
		else:
			ipVersion = False
	#perform individual actions
	if action == 'A':
		if table_type == 'pool':
			Record = DHCP_ip_pool( ip_first	= values['ip_first'],ip_last = values['ip_last'], is_ipv6 = ipVersion, 
				time_created = now, time_modified = now, description = values['description'])
		elif table_type == 'machine':
			Record = DHCP_machine( mac_address = values['mac_address'], ip_address = values['ip_address'], host_name = values['host_name'],
				is_ipv6 = ipVersion, time_created = now, time_modified = now, description = values['description'])
		preparedValues = Record, uname, table_number	
			
	return preparedValues
def extractHostName(hn):
	'''
	Extracts the host name from the input hn. Assumes input will be the format u'host <host-name> {'
	'''
	host = hn.replace('{','')
	host = host.replace('host','')
	host = host.replace(' ','')
	
	return host
	
def extractIPRange(ip_r):
	'''
	Extracts IP range from the input ip_r. Assumes the input will be a python list in the format:
		[ 'range 138.37.53.1 138.37.53.15;', 'range 138.37.54.31 138.37.54.32;' ]
	'''
	ip_unchecked = list()
	ip_checked = list()
	for i in range(len(ip_r)):
		if ip_r[i].find('range') > -1:
			val = ip_r[i].replace('range', '')
			val = val.replace(';','')
			val = val.rstrip(' ')
			val = val.lstrip(' ')
			point = val.find(' ')
			if point > -1:
				ip1 = val[:point].replace(' ','')
				ip2 = val[point:].replace(' ','')
			else:
				ip1 = val.replace(' ','')
				ip2 = ip1				
			#split two addresses
			ip_checked.append((ip1, ip2))
	
	#validate addresses
	for i in range(len(ip_unchecked)):
		try:
			ip1 = IPAddress(ip_unchecked[i][0])
			ip2 = IPAddress(ip_unchecked[i][1])
			ip_checked.append((ip1,ip2))
		except AddrFormatError:
			return False
	return ip_checked
	
def extractMACandIP(macip):
	'''
	Extracts the MAC and IP addresses from the input. May contain more than one IP addresses. Assumes
	the format 'hardware ethernet 00:1c:c0:2c:2d:6d;' for MAC addresses and 'fixed-address 138.37.27.232;' or
	'fixed-address 138.37.27.237, 138.37.16.1, 138.37.17.253, 138.37.18.238, 138.37.19.253;' for IP addresses
	'''
	ip_unchecked = list()
	ip_checked = list()
	mac = ''
	for i in range(len(macip)):
		if macip[i].find('hardware ethernet') > -1:
			val = macip[i].replace('hardware ethernet', '')
			val = val.replace(';','')
			val = val.replace(' ','')
			mac = val
		elif macip[i].find('fixed-address') > -1:
			if macip[i].find(',') > -1: #contains potentially more than one ip
				val = macip[i].replace('fixed-address', '')
				val = val.replace(' ','')
				point = val.find(',')
				while point > -1:
					i = val[:point]
					val = val.replace(i,'')
					val = val.lstrip(',')
					ip_unchecked.append(i)
					point = val.find(',')
					if point == -1:
						val = val.replace(';','')
						ip_unchecked.append(val)
				
			else:
				val = macip[i].replace('fixed-address', '')
				val = val.replace(';','')
				val = val.replace(' ','')
				ip_unchecked.append(val)
	#validate mac and ip address values
	
	if len(mac) == 0:
		return False
	else:
		mac = str(EUI(mac, dialect=mac_custom))

	for i in range(len(ip_unchecked)):
		try:
			ip_checked.append(IPAddress(ip_unchecked[i]))
		except AddrFormatError:
			return False
	return mac, ip_checked
	
def FindValuesFromSplittedLines(splitted_lines, dtype):
	'''
	'''
	dhcp_type = ''
	values = list()
	if dtype is 'host':
		dhcp_type = 'machine'
		hname = extractHostName(splitted_lines[0])
		[macs,ips] = extractMACandIP(splitted_lines[1:])
		if not macs or not ips:
			return False
		else:
			values.append(dhcp_type)
		for i in range(len(ips)):
			dhcp_record = {'host_name': hname, 'mac_address':str(EUI(macs, dialect=mac_custom)), 'ip_address' :ips[i],'description': '' }	
			values.append(dhcp_record)
	elif dtype is 'range':
		dhcp_type = 'ip_pool'
		ip_ranges = extractIPRange(splitted_lines)
		if not ip_ranges:
			return False
		else:
			values.append(dhcp_type)
		for i in range(len(ip_ranges)):
			dhcp_record = {	'ip_first':IPAddress(ip_ranges[i][0]), 'ip_last':IPAddress(ip_ranges[i][1]) ,'description': '' }
			values.append(dhcp_record)
	else:
		pass
		
	return values
	
class Command(LabelCommand):
	def handle_label(self, label, **options):
		print 'Adding data from file: %s' % label
		username = 'admin'
		line_count = 0
		found_list = list()
		not_added = list()
		dhcp_list = list()
		f = open(label, 'r')
		if f:
			for line in f:
				del found_list[:]
				line_count = line_count + 1
				if line[0] == '#':
					pass
				#deal with host parameter
				elif 'host' in line:
					line = line.strip()
					found_list.append(line)
					if line.find('{') > -1:
						n_line = f.next()
						while n_line.find('}') == -1:
							line_count = line_count + 1
							n_line = n_line.strip()
							found_list.append(n_line)
							n_line = f.next()
						Values = FindValuesFromSplittedLines(found_list, 'host')
						if not Values:
							Error = 'Line:%s|%s|IP address or machine name is invalid.' % (line_count, line)
							not_added.append(Error)
						else:
							dhcp_list.append(Values)
					else:
						Error = 'Line:%s|%s|Incorrectly formatted line' % (line_count, line)
						not_added.append(Error)	
						pass
				#deal with subnet-range and subnet-pool-range parameters
				elif 'subnet' in line:
					line = line.strip()
					if line.find('{') > -1:
						n_line = f.next()
						while n_line.find('}') == -1:
							n_line = n_line.strip()
							if n_line.find('range') > -1:
									found_list.append(n_line)
							elif n_line.find('pool') > -1:
								if n_line.find('{') > -1:
									n_line = f.next()
									while n_line.find('}') == -1:
										n_line = n_line.strip()
										if n_line.find('range') > -1:
											found_list.append(n_line)
										n_line = f.next()
									#find range in pool
								else:
									Error = 'Line:%s|%s|Incorrectly formatted line' % (line_count, line)
									not_added.append(Error)	
									pass
							n_line = f.next()
						Values = FindValuesFromSplittedLines(found_list, 'range')
						if not Values:
							Error = 'Line:%s|%s|Could not find IP range or IP addresses are invalid' % (line_count, line)
							not_added.append(Error)
						else:
							dhcp_list.append(Values)
					else:
						Error = 'Line:%s|%s|Incorrectly formatted line' % (line_count, line)
						not_added.append(Error)	
						pass
				else:
					pass			
			f.close()
			#start writing a log of events
			filename = "LoadDHCPdataLog.log"
			FILE = open(filename,"w")
			now = datetime.datetime.now()
			logstring = '%s: Successfully scanned file %s\n' % (now, label)
			FILE.write(logstring)
			confirm = True
			adminUser = User.objects.get(username__exact = username)
			#add to DHCP database
			if not_added:
				logstring = '%s: Error in formatting - could not add the following records:\n' % now
				print logstring
				FILE.write(logstring)
				for record in not_added:
					print record
					FILE.write(record + '\n')
				done = 0
				while not done:
					rslt = raw_input("Do you want to proceed without adding these records? (hint: \"yes\" or \"no\"): ")
					if rslt == 'yes':
						confirm = True
						break
					elif rslt == 'no':
						print 'User cancelled...'
						logstring = 'User cancelled...' 
						FILE.write(logstring + '\n')
						confirm = False
						break
			else:
				logstring = '%s: No errors founded during initial scan :o) \n' % now
				FILE.write(logstring)
				
			if confirm:
				done = 0
				while not done:
					rslt = raw_input("There are a total of %s records that have been found. Do you want to add these? (hint: \"yes\" or \"no\"): " % len(dhcp_list))
					if rslt == 'yes':
						#Enter all records in database						
						check_dns_list = list()
						line_count = 0
						error_count = 0
						for record in dhcp_list:		
							#[unique, unique_error] = DNS_name.objects.is_unique(record['ip_address'],record['name'],record['dns_type'], '', True)	
							for i in range(len(record)):
								if not i == 0:	
									if record[0] == 'machine':
										[unique, unique_error] = DHCP_machine.objects.is_unique(adminUser, record[i]['ip_address'], record[i]['mac_address'], '')
										if unique:
											#AddAndLogRecord('DHCP_machine', DHCP_machine, 'admin', record[i])
											AddAndLogRecord(prepare_values('A', 'machine', record[i], username, ''))
											#print record[i]
										 	line_count = line_count + 1
										else:
											error_count = error_count + 1
											logstring = '%s|Error|: MAC Address %s, IP Address: %s | could not save to database - %s.' %(now,record[i]['mac_address'], record[i]['ip_address'], unique_error )
											FILE.write(logstring + '\n')
											print logstring
									elif record[0] == 'ip_pool':
										[unique, unique_error] = DHCP_ip_pool.objects.is_unique(adminUser, record[i]['ip_first'], record[i]['ip_last'], '')
										if unique:
											#AddAndLogRecord('DHCP_ip_pool', DHCP_ip_pool, 'admin', record[i])
											AddAndLogRecord(prepare_values('A', 'pool', record[i], username, ''))
											#print record[i]
										 	line_count = line_count + 1
										else:
											error_count = error_count + 1
											logstring = '%s|Error|: IP Range %s - %s | could not save to database - %s.' %(now,record[i]['ip_first'], record[i]['ip_last'], unique_error )
											FILE.write(logstring + '\n')
											print logstring
				
						logstring = 'Total DHCP records: %s' %len(dhcp_list)
						FILE.write(logstring + '\n')
						logstring = 'Total Successfully created: %s' % line_count	
						FILE.write(logstring + '\n')
						logstring = 'Total in Error: %s' % error_count		
						FILE.write(logstring + '\n')
						break
					elif rslt == 'no':
						print 'User cancelled...'
						logstring = 'User cancelled...' 
						FILE.write(logstring + '\n')
						break
		else:
			print 'File "%s" could not be opened' % label

