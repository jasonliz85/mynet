from django.db import models
from netaddr import IPAddress

class NameManager(models.Manager):
	def is_unique(self, ip, mname, dt):
		'''
		Checks the uniqueness of a record based on the ip address, machine name and dns type. 
		'''
		unique = False
		valip = self.filter(ip_address = ip).count()
		valnm = self.filter(name = mname).count()
		if dt == '1BD':
			if not valip:
				if not valnm:
					unique = True
		elif dt == '2NA':
			if not valnm:
		   		unique = True	
		else:
			if not valip:
				unique = True
			
		return unique
		
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
