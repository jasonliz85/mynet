#This is the object manager for models.py
from django.db import models
from netaddr import *
from subnets.AccessControl.views import is_ipaddress_in_netresource, is_name_in_netresource, get_address_blocks_managed_by, get_dns_patterns_managed_by
from django.db.models import Q
class NameManager(models.Manager):
	def is_unique(self, ip, mname, dt, mid, enable_softcheck):
		'''
		Checks the uniqueness of a record based on the ip address (ip, assummed netaddr IPAddress object), machine name (mname) and dns type (dt).
		Returns True if unique, False otherwise.
		By default, this function will perform a hard check based on a strict non-duplicated record (i.e. if ip, mname and dt are not already
		in the database). If enable_softcheck is True, this function will also perform the following:
		#3. Apply softer check, in three parts
		# a.if type is address to name, must check that the ip address is NOT mapped to another name (i.e. one address to one name)
		# b.if type is name to address, must check that the name is NOT mapped to another ip address (i.e. one name to one address)
		# c.if type is bi-directional, must check for both conditions a AND b
		'''
		#Algorithm
		#I.Initialise variables
		unique = True
		unique_error = ''
		#1.First, retrieve all records accosiated with ip and name
		try:
			found_ip = self.filter(ip_address = ip).exclude(id = mid) 	#found ip addresses
			found_nm = self.filter(name = mname).exclude(id = mid) 		#found machine names
		except ValueError:
			found_ip = self.filter(ip_address = ip)				#found ip addresses
			found_nm = self.filter(name = mname)				#found machine names
		#Deal with empty querysets
		if not len(found_ip) and len(found_nm):
			found_records = found_nm
		elif not len(found_nm) and len(found_ip):		
			found_records = found_ip
		elif not len(found_nm) and not len(found_ip): 	
			return unique, unique_error
		else:	
			found_records = found_ip|found_nm
				
		#2.Do a hard check - strictly no like for like duplicated records
		for record in found_records:
			if record.ip_address == ip and record.name == mname and record.dns_type == dt:
				unique = False
				unique_error = "You cannot create this record because it already exists. DNS ID: " + str(record.id)
				return unique, unique_error

		#3.If enabled, apply softer check
		if enable_softcheck:
			if dt == '3AN': 	#address to name 	
				for record in found_records:
					if record.dns_type == dt and record.ip_address == ip:
						unique = False
						unique_error = "This IP address has aleady been assigned to another name, " + record.name
						break
			elif dt == '2NA': 	#name to address
				for record in found_records:
					if record.dns_type == dt and record.name == mname: 
						unique = False
						unique_error = "This name has aleady been assigned to another IP address, " + str(IPAddress(record.ip_address))
						break
			else: 			#else bi directional
				for record in found_records:
					if record.dns_type == dt and record.ip_address == ip and record.name == mname:
						unique = False
						unique_error = "This machine name and IP address has already been assigned and therefore cannot be changed to a bidirectional record." + "\n"+ record.name + "<->" + str(IPAddress(record.ip_address))
						break
					elif record.dns_type == dt and record.ip_address == ip:
						unique = False
						unique_error = "This IP address has aleady been assigned to another name, " + record.name + ". Both IP address and machine name must be unique for a bi-directional record."
						break
					elif record.dns_type == dt and record.name == mname:
						unique = False
						unique_error = "This name has aleady been assigned to another IP address, " + str(IPAddress(record.ip_address)) + ". Both IP address and machine name must be unique for a bi-directional record."
						break					
		return unique, unique_error
	def is_permitted(self, request, ip_address, name, dns_typ):
		"""
		This function checks the name, ipaddress and dns type to see the record is allowed to be created. There are three check, stated below:
			bi-directional - two checks on each record is needed | permission for both ip address and machine name
			address to name - check only pefrom subnets.DNS.models import *rmission for ip address
			name to address - check only permisiion for machine name
		"""
		has_permission = False	
		custom_errors = ""#list()
		errors = ""
		msg1 = "You are not allowed to add this "
		msg2 = ", it is not part of your network resource group."
		[check1, blank] = is_ipaddress_in_netresource(request, ip_address)
		check2 = is_name_in_netresource(request, name)
		if dns_typ == '1BD':
			if check1 == True and check2  == True:
				has_permission = True
			if not check1:
				errors = "IPAddress: " + str(IPAddress(ip_address))
			if not check2:
				if len(errors) > 0:
					errors = errors + " and Machine Name: " + name
				else:
					errors = "Machine Name: " + name
		elif dns_typ == '2NA':
			if check2 == True:
				has_permission = True
			if not check2:
				errors = "Machine Name: " + name
		else:
			if check1 == True:
				has_permission = True
			if not check1:
				errors = "IPAddress: " + str(IPAddress(ip_address))
	
		custom_errors = msg1 + errors + msg2
		return has_permission, custom_errors
	def get_permitted_records(self, request, enable_type_filter, order_by, order_dir, change_dir):
		"""
		This function return a queryset from the model table DNS_name. The returned results are filtered by permitted
		ip_blocks, dns_expressions and dns_type that the user is able to access. If enable_type_filter is enabled, 
		a further filtering step is applied - please see comments this function for further information.
		order_by - order by ip:ip_address, mac:mac_address, time:time_created
		order_dir - asc:ascending or desc:descending
		change_dir -
		"""
		import operator
		total_AN_finds = []
		total_NA_finds = []
		total_BD_finds = []
		permitted_records = []
		if order_by == 'ip':
			var = "ip_address"
		elif order_by == 'vers':
			var = "is_ipv6"
		elif order_by == 'name':
			var = "name"
		else:
			var = "time_created"
			
		if order_dir == 'desc':
			var = "-"+var
		#1.Get network groups, ip blocks and dns expressions which the user has permission to control
		ip_blocks = get_address_blocks_managed_by(request.user)
		dns_exprs = get_dns_patterns_managed_by(request.user)

		#2.First build complex query for subnets and dns expressions
		#a.subnets
		blocks = [ IPNetwork(str(b)) for b in ip_blocks ]
		blocks = cidr_merge(blocks)
		complex_subnet_queries = [ Q(ip_address__gte = ip_block[0]) & Q(ip_address__lte = ip_block[-1]) for ip_block in blocks ]
		#b.dns expressions
		complex_name_queries = list()
		for expression in range(len(dns_exprs)):
			dns_filter = Q(name__regex = ('\S' + str(dns_exprs[expression])))
			complex_name_queries.append(dns_filter)
		#3.Second, apply three database queries, 
		#	1: for all records with dns type address to name, apply complex_subnet_queries #operator.or_
		#	2: for al564 records in total l records with dns type name to address, apply complex_name_queries
		#	3: for all records with dns type bidirectional, apply complex_subnet_queries and complex_name_queries
		if len(complex_subnet_queries):
			total_AN_finds = self.filter(reduce(operator.or_, complex_subnet_queries),	dns_type = '3AN')
		if len(complex_name_queries):
			total_NA_finds = self.filter(reduce(operator.or_, complex_name_queries),	dns_type = '2NA')
		if len(complex_subnet_queries) and len(complex_name_queries):
			total_BD_finds = self.filter(reduce(operator.or_, complex_name_queries), 	reduce(operator.or_, complex_subnet_queries), 
										dns_type = '1BD')
		#4.combine records and order
		if len(total_AN_finds) or len(total_NA_finds) or len(total_BD_finds):
			permitted_records = total_AN_finds | total_NA_finds | total_BD_finds
		if len(permitted_records):
			permitted_records = permitted_records.order_by(var)								

		return permitted_records
