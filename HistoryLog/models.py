from django.db import models
from subnets.AccessControl.models import *
from django.contrib.auth.models import Group, User

class netgroup(models.Model):
	name = models.CharField('Network Group Name', max_length=50)
	def __unicode__(self):
		return u'%s' % (self.name)

class usrname(models.Model):
	uname = models.CharField('User Name', max_length=50)
	def __unicode__(self):
		return u'%s' % (self.uname)
	
class log(models.Model):
	ACTION_CHOICES = ( 
			('A', 'Created'), 	# added a record in model
		        ('D', 'Deleted'), 	# deleted a record in model
			('E', 'Modified'), 	# edited a record in model
			('R', 'Redo'),  # redo a previous action in log
			('U', 'Undo'), 	# undo a previous action in log
			)
	MODEL_CHOICES = (
			('1','DNS Names'),
			('2','DHCP IP Pools'),
			('3','DHCP Machines')
	)
	#NetGroupName 	= models.ManyToManyField(Group, blank=True)
	TableName	= models.CharField('Table Name',max_length = 1, choices = MODEL_CHOICES)
	RecordID	= models.IntegerField('Table RecordAction ID')
	NetUser		= models.ForeignKey(User, blank=True)
	TimeOccured	= models.DateTimeField()
	ActionType	= models.CharField('Action', max_length = 1, choices = ACTION_CHOICES)	
	ValuesBefore	= models.CharField('Before',max_length = 500, blank=True, null=True)
	ValuesAfter	= models.CharField('After',max_length = 500, blank=True, null=True)	
	IsBulk		= models.BooleanField('Bulk Upload')
	def __unicode__(self):
		return u' %s %s' % ( self.NetUser, self.TimeOccured)

	class Meta:
        	ordering = ['-TimeOccured']
	
