from django.db import models
from netaddr import IPAddress

class NameManager(models.Manager):
	def is_unique(self, ip, mname, dt, mid, enable_softcheck):
		'''
		Checks the uniqueness of a record based on the ip address (ip, assummed in integer form), machine name (mname) and dns type (dt).
		Returns True if unique, False otherwise.
		By default, this function will perform a hard check based on a strict non-duplicated record (i.e. if ip, mname and dt are not already
		in the database). If enable_softcheck is True, this function will also perform the following:
		#3.Apply softer check, in three parts
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
		found_records = found_ip|found_nm
		if not found_records:
			return unique, unique_error
		#2.Do a hard check - strictly no like for like duplicated records
		for record in found_records:
			if record.ip_address == ip and record.name == mname and record.dns_type == dt:
				unique = False
				unique_error = "Duplication error, this record already exists. DNS ID: ", record.id
#			elif record.ip_address == ip and record.dns_type == dt:
#				unique = False
#				unique_error = "Duplication error, this IP address already exists."
#			elif record.name == mname and record.dns_type == dt:
#				unique = False
#				unique_error = "Duplication error, this machine name already exists."
		#3.If enabled, apply softer check
		if enable_softcheck:
			if dt == '3AN': 	#address to name 				
				for record in found_records:
					if record.name == mname:
						unique = False
						unique_error = "This IP address has already been mapped to another machine name, ", record.name
						break
			elif dt == '2NA': 	#name to address
				for record in found_records:
					if record.ip_address == ip:
						unique = False
						unique_error = "This machine name has already been mapped to another IP address, ", record.ip_address
						break
			else: 			#else bi directional
				for record in found_records:
					if record.ip_address == ip and record.name == mname:
						unique = False
						unique_error = "This machine name and IP address already exists and cannot be changed to a bi directional record."
						break
					elif record.ip_address == ip:
						unique = False
						unique_error = "This IP address already exists. Both IP address and machine name must be unique for a bi-directional record."
						break
					elif record.name == mname:
						unique = False
						unique_error = "This machine name already exists. Both IP address and machine name must be unique for a bi-directional record."
						break
					
		return unique, unique_error
		
class DNS_name(models.Model):							#DNS NAMING MODEL
	name 		= models.CharField('DNS name', max_length = 255)	#DNS name regular expression
	ip_address	= models.IntegerField('IP address')			#DNs ip address pair
	dns_type	= models.CharField('Type', max_length = 3 )		#DNS type
	description 	= models.TextField('Description', blank=True, null=True)#DNS name description
	is_ipv6 	= models.BooleanField()					#DNS bool check IP version 6
	time_created 	= models.DateTimeField()				#DNS name creation time
	time_modified  	= models.DateTimeField()				#DNS name modification time
	objects 	= NameManager()
	def LogRepresentation(self):
		return u'{\'name\':\'%s\', \'ip_address\':%s, \'dns_type\':\'%s\', \'description\':\'%s\'}' % (self.name, self.ip_address, self.dns_type, self.description )
	def __unicode__(self):
		return u'\'name\':\'%s\',\'ip_address\':\'%s\',\'is_ipv6\':\'%s\',\'dns_type\':\'%s\',\'description\':\'%s\''% (self.name, str(IPAddress(self.ip_address)), self.is_ipv6, self.dns_type, self.description)
	class Meta:
        	ordering = ['ip_address','dns_type']
        	
        #ipaddress object to string hex 
	#var1 = '%032x' % IPAddress('').value
	#string hex to ipaddress object
	#var2 = IPAddress(int(var1, 16))
