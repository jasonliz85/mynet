from django.db import models

class DNS_names(models.Model):							#DNS NAMING MODEL
	machine_name 	= models.CharField('DNS name', max_length = 30)		#DNS name regular expression
	ip_pair		= models.IntegerField('IP address')			#DNs ip address pair
	dns_type	= models.CharField('Type', max_length = 3 )		#DNS type
	description 	= models.TextField('Description', blank=True, null=True)#DNS name description
	is_ipv6 	= models.BooleanField()					#DNS bool check IP version 6
	time_created 	= models.DateTimeField()				#DNS name creation time
	is_active 	= models.BooleanField()					#DNS reg active

	def LogRepresentation(self):
		return u'{\'machine_name\':\'%s\', \'ip_pair\':%s, \'dns_type\':\'%s\', \'description\':\'%s\'}' % (self.machine_name, self.ip_pair, self.dns_type, self.description )
	def __unicode__(self):
		return u'\'machine_name\':\'%s\',\'ip_pair\':\'%s\',\'is_ipv6\':\'%s\',\'dns_type\':\'%s\',\'description\':\'%s\''% (self.machine_name, str(IPAddress(self.ip_pair)), self.is_ipv6, self.dns_type, self.description)
	class Meta:
        	ordering = ['ip_pair','dns_type']
