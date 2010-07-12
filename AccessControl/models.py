from django.db import models

#register a machine on DHCP server
class test_machine(models.Model):
	MAC_pair	= models.CharField('MAC Address',max_length = 12)	#MAC address 
	IP_pair		= models.IPAddressField('IP Address')			#IP address 
	PC_pair		= models.CharField('PC Name',max_length = 12)		#PC name
	description 	= models.TextField(blank=True, null=True)		#description of machine (optional)
	def __unicode__(self):
		return u'%s-%s-%s' % (self.MAC_pair, self.IP_pair, self.PC_pair)

class DHCP_machine(models.Model):
	MAC_pair	= models.CharField('MAC Address',max_length = 12)	#MAC address 
	IP_pair		= models.IPAddressField('IP Address')			#IP address 
	PC_pair		= models.CharField('PC Name',max_length = 12)		#PC name
	time_created 	= models.DateTimeField()				#registration creation time
	time_deleted 	= models.DateTimeField(blank=True, null=True)		#registration deletion time
	description 	= models.TextField(blank=True, null=True)		#description of machine (optional)
	#to add date_modified
	def __unicode__(self):
		return u'%s-%s-%s %s, %s' % (self.MAC_pair, self.IP_pair, self.PC_pair, self.time_created,self.time_deleted )


