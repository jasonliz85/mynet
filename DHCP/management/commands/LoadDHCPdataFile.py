from django.core.management.base import LabelCommand
from netaddr import *
class mac_custom(mac_unix): pass
mac_custom.word_fmt = '%.2X'

def extractHostName(hn):
	'''
	Extracts the host name from the input hn. Assumes input will be the format u'host <host-name> {'
	'''
	host = hn.replace('{','')
	host = host.replace('host','')
	host = host.replace(' ','')
	
	return host
	
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
		if macs == False or ips == False:
			return False
		for i in range(len(ips)):
			dhcp_record = {'host_name': hname, 'mac_address':str(EUI(macs, dialect=mac_custom)), 'ip_address' :ips[i],'description': '' }	
			values.append([dhcp_type, dhcp_record])
		
	elif dtype is 'range':
		dhcp_type = 'ip_pool'
		pass
	else:
		pass
		
	return values
	
class Command(LabelCommand):
	def handle_label(self, label,**options):
		print 'Adding data from file: %s' % label
		line_count = 0
		found_list = list()
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
						print Values
					else:
						pass	
				#deal with subnet-range parameters
				elif 'subnet' in line:
					line = line.strip()
					if line.find('{') > -1:
						n_line = f.next()
						#print line
						while n_line.find('}') == -1:
							n_line = n_line.strip()
							#print n_line
							n_line = f.next()
						#print '}'
					else:
						pass
				#deal with pool-range parameters
				elif 'pool' in line:
					line = line.strip()
					#print 'Pool-range'
					pass
				else:
					pass			
			f.close()
			#add to DHCP database
		else:
			print 'File "%s" could not be opened' % label

