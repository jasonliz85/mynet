from django.core.management.base import LabelCommand
from netaddr import *
from string import replace, lstrip, rstrip
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
	print section
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
		first_points = ip_reversed.find('.')
		find_point = 0
		while (find_point == -1):
			find_point = ip_reversed.find('.')
			ip_normal = ip_reversed[0:find_point] + ip_normal
			
		while (find_point > -1):
		... 	find_point = test2.find('.')
		... 	ip_normal = test2[0:find_point] + ip_normal
		... 	test2 = test2.replace(test2[0:find_point], '')
		... 	test2 = test2.lstrip('.')
		... 	print test2

		print points
	
	print ip_normal
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
	values = {'dns_type': '', 'ip_address':'', 'name':'', 'ttl': ''}
	
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
		print values
		return False
	else:
		return values

class Command(LabelCommand):
	def handle_label(self, label,**options):
		print 'Adding data from file: %s' % label
		line_count = 0
		f = open(label, 'r')
		if f:
			for line in f:
				line_count = line_count + 1
				if line[0] == ('^' or '+' or '='):
					line = line.strip()
					#find variables in the line - dns type, ip address, machine name, ttl field, 
					splitted = line[1:].split(':')
					Values = FindValuesFromSplittedLine(line[0], splitted)
					#If Values returns False, then could not successfully identify both machine name and ip address
					if not Values:
						print line
						print Values
						print 'Error: Could not find either the machine name or ip address from line "%s"' % line_count
						break
				else:
					pass
			f.close()
		else:
		    print 'Error: File "%s" could not be opened' % label
	

