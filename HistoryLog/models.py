from django.db import models
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
			('A', 'ADD'), 	# added a record in model
		        ('D', 'DEL'), 	# deleted a record in model
			('E', 'EDIT'), 	# edited a record in model
			)
	#NetGroupName 	= models.ManyToManyField(Group, blank=True)
	#TableName	= models.CharField('Table Name',max_length = 50)
	NetUser		= models.ForeignKey(User, blank=True)
	TimeOccured	= models.DateTimeField()
	ActionType	= models.CharField('Action', max_length = 1, choices = ACTION_CHOICES)	
	ValuesBefore	= models.CharField('Before',max_length = 500, blank=True, null=True)
	ValuesAfter	= models.CharField('After',max_length = 500, blank=True, null=True)	
	IsBulk		= models.BooleanField()
	def __unicode__(self):
		return u' %s %s' % ( self.NetUser, self.TimeOccured)

	class Meta:
        	ordering = ['TimeOccured']
	
