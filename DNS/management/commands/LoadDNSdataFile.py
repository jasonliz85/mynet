from django.core.management.base import LabelCommand
from django.contrib.auth.models import User
from subnets.DNS.models import *
from subnets.helper_views import AddAndLogRecord
from netaddr import *
import datetime
#from string import replace, lstrip, add

def prepare_values(action, vals, uname, m_id):
	'''
	Prepares the values, so as to be returned to the funtion AddAndLogRecord or EditAndLogRecord
	Arguments:
		action - 'A' Adding, or 'E' editing
		vals - values to add to the database
		uname - django username objects
		m_id - if editing, specified the id of the record to be modified
	'''
	now = datetime.datetime.today()
	is_bulk = True
	table_number = '1' #for logging purposes
	values = { 'name':vals['name'],'dns_type':vals['dns_type'],
		'ip_address':IPAddress(vals['ip_address']),'description':vals['description'],'ttl': vals['ttl'] }
		
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
		
	return preparedValues
	
def CheckIPAddress(section):
	'''
	Returns True if 'section' is a valid ip version 4 address (ip address must be not be version 6)
	'''
	try:
		ip = IPAddress(section)
	except AddrFormatError:
		return False
	
	if ip.version == 6:
		return False
	else:
		return True
def CheckReverseLookup(section):
	'''
	Returns True if 'section' is a valid dns ip reverse lookup address. section can be ip version 4 or 6.
	'''

	if section.find('.ip6.arpa') > -1:
		return True
	elif section.find('.in-addr.arpa') > -1:
		return True
	else:
		return False
def is_ipv6_check(val):
	if val.find('.ip6.arpa') > -1:
		return True
	else:
		return False

def FormatReverseLoopup(section):
	'''
	Returns the 'normal' format of the dns reverse lookup address. Applies another check to make certain formatted
	value is correct
	'''
	ip_normal = ''
	#strip string end values '.in-addr.arpa' and '.ip6.arpa'and reverse the result
	#must deal with Ipv6 and ipv4 separately
	if is_ipv6_check(section): #ipv6
		ip_reversed = section.replace('.ip6.arpa','')
		ip_reversed = ip_reversed.replace('.','')
		for i in range(31,-1,-4):
			if i == 3:
				ip_normal = ip_normal + ip_reversed[i::-1]
			else:
				ip_normal = ip_normal + ip_reversed[i:i-4:-1] + ':'
	else: #ipv4
		ip_reversed = section.replace('.in-addr.arpa','')
		find_point = ip_reversed.find('.')
		while find_point > -1:
			ip_normal = '.' + ip_reversed[0:find_point:] +  ip_normal
			ip_reversed = ip_reversed.replace(ip_reversed[0:find_point:], '', 1)
			ip_reversed = ip_reversed.lstrip('.')
			find_point = ip_reversed.find('.')
			if find_point == -1:
				ip_normal = ip_reversed + ip_normal
	#check if the results when reversed matches the exactl value of the input section
	try:
		ip_normal_revered = IPAddress(ip_normal).reverse_dns
	except AddrFormatError:
		return False
	#strip '.' at the end
	ip_normal_revered = ip_normal_revered.rstrip('.')
	#test condition
	if not ip_normal_revered == section:
		return False
	else:
		return IPAddress(ip_normal)
	
def FindValuesFromSplittedLine(dns_type, splitted_line):
	'''
	To comment:
	'''
	#dns values to be populated, ttl is not neccessary and is optional
	values = {'dns_type': '', 'ip_address':'', 'name':'', 'ttl': 0, 'description':''}
	
	if dns_type == '+':
		values['dns_type'] = '2NA'
	elif dns_type == '=':
		values['dns_type'] = '1BD'
	elif dns_type == '^':
		values['dns_type'] = '3AN'
	
	
	for i in range(len(splitted_line)):
		if i == 0:	
			#if '^', we should be expecting the ip address first in 
			#reverse ip lookup format (i.e. '13.0.24.172.in-addr.arpa'
			#or d.e.a.d.b.e.e.f.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.e.f.ip6.arpa' )
			if dns_type == '^':
				if CheckReverseLookup(splitted_line[i]):
					values['ip_address'] = FormatReverseLoopup(splitted_line[i])
					if values['ip_address'] == False:
						values['ip_address'] = 'INVALID'
				else:
					values['ip_address'] = 'INVALID'
			#else we should assume that the first section of the split is the machine name 
			#i.e. either a bi directional record or name to address record
			else:
				values['name'] = splitted_line[i]
		elif i == 1:
			#if '^', we should be expecting the machine name in 
			#the second section of the splitted line
			if dns_type == '^':
				values['name'] = splitted_line[i].rstrip('.')
			#else we should assume that this section is an ip address
			else:
				if CheckIPAddress(splitted_line[i].rstrip('.')):
					values['ip_address'] = IPAddress(splitted_line[i].rstrip('.'))
				else:
					values['ip_address'] = 'INVALID'
		else:
			try:
				values['ttl'] = int(splitted_line[i])
			except ValueError:
				pass
	
	if values['ip_address'] == '' or values['name'] == '' or values['dns_type'] == '':
		return 'SKIP'
	elif values['ip_address'] == 'INVALID':
		#print values
		return False
	else:
		return values

class Command(LabelCommand):
	def handle_label(self, label,**options):
		print 'Adding data from file: %s' % label
		username = 'bulk_import_user'
		try:
			adminUser = User.objects.get(username__exact = username)
		except User.DoesNotExist:
			print 'Warning: User %s does not exist\nCreating...' %username
			try:
				adminUser = User.objects.create_user(username, 'admin@qmul.ac.uk', 'password')
				adminUser.save
			except:
				print 'Error: Problems creating user %s.'%username
				return
		try :
			f = open(label, 'r')
		except TypeError:
			print 'Error: Incorrect file destination'
			return
		line_count = 0
		dns_list = list()
		not_added = list()
		if f:
			#Find All Records to be Added
			for line in f:
				line_count = line_count + 1
				line = line.strip()
				if line[0] in ['^', '+', '=']:
					#find variables in the line - dns type, ip address, machine name, ttl field, 
					splitted = line[1:].split(':')
					Values = FindValuesFromSplittedLine(line[0], splitted)
					#If Values returns False, then could not successfully identify both machine name and ip address
					if not Values:
						Error = 'Line:%s|%s|IP address or machine name is invalid.' % (line_count, line)
						not_added.append(Error)
					else:
						dns_list.append(Values)
				else:
					pass
			f.close()
			filename = "LoadDNSdataLog.log"
			FILE = open(filename,"w")
			now = datetime.datetime.now()
			logstring = '%s: Successfully scanned file %s\n' % (now, label)
			FILE.write(logstring)
			confirm = True
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
					if rslt == "yes":
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
					rslt = raw_input("There are a total of %s records that have been found. Do you want to add these? (hint: \"yes\" or \"no\"): " % len(dns_list))
					if rslt == "yes":
						#Enter all records in database						
						check_dns_list = list()
						line_count = 0
						error_count = 0
						for record in dns_list:		
							[unique, unique_error] = DNS_name.objects.is_unique(record['ip_address'],record['name'],record['dns_type'], '', True)	
							if unique:
								#AddAndLogRecord('DNS_name', DNS_name, 'admin', record)
								AddAndLogRecord(prepare_values('A', record, adminUser, ''))
							 	line_count = line_count + 1
							else:
								error_count = error_count + 1
								logstring = '%s|Error|Machine Name: %s, IP Address: %s, DNS type:%s | could not save to database - %s.' %(now,record['name'], record['ip_address'],record['dns_type'], unique_error )
								FILE.write(logstring + '\n')
								#print logstring
				
						logstring = 'Total DNS records: %s' %len(dns_list)
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
			FILE.close()
		else:
		    print 'Error: File "%s" could not be opened' % label
	

