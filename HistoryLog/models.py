from django.db import models
from subnets.AccessControl.models import *
from subnets.AccessControl.views import *
from django.contrib.auth.models import Group, User
from django.db.models import Q
class LogManager(models.Manager):
	def get_permitted_logs(self, user_object, order_by, order_dir, change_dir):
		import operator
		complex_queries = list()
		total_LOG_finds = []
		if order_by == 'act':
			var = "ActionType"
		elif order_by == 'tabl':
			var = "TableName"
		elif order_by == 'user':
			var = "NetUser"
		elif order_by == 'time':
			var = "TimeOccured"
		if order_dir == 'desc':
			var = "-"+var
		print var
		ip_blocks = get_address_blocks_managed_by(user_object)
		dns_exprs = get_dns_patterns_managed_by(user_object) 
		net_group = get_netgroups_managed_by_user(user_object)

		for ip_block in ip_blocks:
			complex_queries.append(Q(NetResource_ipsubnets__id__exact = ip_block.id))	
		for expression in dns_exprs:
			complex_queries.append(Q(NetResource_dnsexpressions__id__exact = expression.id))	
		if len(complex_queries):
			total_LOG_finds = self.filter(reduce(operator.or_, complex_queries), IsBulk = False).distinct()
		if len(total_LOG_finds):
			total_LOG_finds = total_LOG_finds.order_by(var)	
		return total_LOG_finds
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
		('R', 'Redo'), 		# redo a previous action in log
		('U', 'Undo'), 		# undo a previous action in log
		)
	MODEL_CHOICES = (
		('1','DNS Names'),
		('2','DHCP IP Pools'),
		('3','DHCP Machines')
	)
	NetResource_ipsubnets = models.ManyToManyField(ip_subnet)
	NetResource_dnsexpressions = models.ManyToManyField(dns_expression)
	TableName	= models.CharField('Table Name',max_length = 1, choices = MODEL_CHOICES)
	RecordID	= models.IntegerField('Table Record')
	NetUser		= models.ForeignKey(User, blank=True)
	TimeOccured	= models.DateTimeField()
	ActionType	= models.CharField('Action', max_length = 1, choices = ACTION_CHOICES)	
	ValuesBefore= models.CharField('Before',max_length = 500, blank=True)
	ValuesAfter	= models.CharField('After',max_length = 500, blank=True)	
	IsBulk		= models.BooleanField('Bulk Upload')
	objects 	= LogManager()
	def __unicode__(self):
		return u' %s %s' % ( self.NetUser, self.TimeOccured)
	class Meta:
        	ordering = ['-TimeOccured']
	

