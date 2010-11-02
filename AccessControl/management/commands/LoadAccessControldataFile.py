from netaddr import *
from django.core.management.base import LabelCommand
from subnets.AccessControl.views import add_ip_subnet

import datetime
def extractSubnet(sn):
	'''
	Extracts the Subnet from the input. Assumes the input is unclean and may look like this: ' 194.83.102.156/30       '.
	Input may also have tabs '\t', white spaces ' ', commas ',', or a pipe '|'. This function also performs a check 
	on the input subnet to see if it is valid.
	'''
	subnet = sn.strip()
	subnet = subnet.replace('|','')
	subnet = subnet.replace(',','')
	subnet = subnet.replace('\t','')
	try:
		IPNetwork(subnet)
	except:
		return False
	return subnet
def extractDescription(dscr):

	description = ''
	for i in range(len(dscr)):
		dscr[i] = dscr[i].replace('|','')
		dscr[i] = dscr[i].replace('\t','')
		dscr[i] = dscr[i].strip()
		if i == 0:
			description = description + dscr[i]
		else:
			description = description + ' | ' + dscr[i]	
	return description
def FindValuesFromSplittedLine(splitted_line):
	'''
	Extracts the VLan (if present), IP subnet, and description from the input 'splitted_line'.
	'''
	subnet = ''
	dscr = ''
	vlan = 0
	for i in range(len(splitted_line)):
		if i == 0:
			try:
				vlan = int(splitted_line[i])
			except ValueError:
				vlan = 0
		elif i == 1:
			subnet = extractSubnet(splitted_line[i])
			if not subnet:
				return False
		else:
			dscr = extractDescription(splitted_line[i:])
			break
	values = {'vlan':vlan, 'ip_value':subnet, 'description':dscr}
	return values
	
class Command(LabelCommand):
	def handle_label(self, label,**options):
		print 'Adding data from file: %s' % label
		line_count = 0
		not_added = list()
		subnet_list = list()
		found_list = list()
		f = open(label, 'r')
		if f:
			for line in f:
				del found_list[:]
				line_count = line_count + 1
				if line_count == 1 or line[0] in ['#', '-']:
					pass
				else:
					stripped = line.strip()
					point =  stripped.find('|')
					while point > -1:
						var = stripped[:point]
						found_list.append(var)
						stripped = stripped[point:].lstrip('|')
						point = stripped.find('|')
						if point == -1:
							found_list.append(stripped)
					if not found_list:
						pass
					else:
						Values = FindValuesFromSplittedLine(found_list)
						if not Values:
							Error = 'Line:%s|%s|Invalid formating or incorrect subnet.' % (line_count, line)
							not_added.append(Error)
						else:
							subnet_list.append(Values)
			f.close()
			filename = "LoadAccessControldataLog.log"
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
					rslt = raw_input("There are a total of %s records that have been found. Do you want to add these? (hint: \"yes\" or \"no\"): " % len(subnet_list))
					if rslt == 'yes':
						#Enter all records in database						
						check_dns_list = list()
						line_count = 0
						error_count = 0
						for record in subnet_list:		
							[unique, unique_error] = add_ip_subnet(record)
							if unique:
							 	error_count = error_count + 1
								logstring = '%s|Error|: subnet %s | could not save to database - %s.' %(now,record['ip_value'], unique_error )
								FILE.write(logstring + '\n')
								print logstring
							else:
								line_count = line_count + 1
						logstring = 'Total subnet records: %s' %len(subnet_list)
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
	
