from django.db import models

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
	NetGroupName 	= models.ForeignKey(netgroup)
	NetUser 	= models.OneToOneField(usrname)
	TimeOccured	= models.DateTimeField()
	ActionType	= models.CharField(max_length = 1, choices = ACTION_CHOICES)	
	ValuesBefore	= models.CharField(max_length = 500)
	ValuesAfter	= models.CharField(max_length = 500)
	#TableName	= models.CharField(max_length = 50)
	#IsBulk		= models.BooleanField()
	def __unicode__(self):
		return u'%s %s %s' % (self.NetGroupName, self.NetUser, self.TimeOccured)

	class Meta:
        	ordering = ['TimeOccured']
	
