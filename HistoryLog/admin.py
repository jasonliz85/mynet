from django.contrib import admin
from subnets.HistoryLog.models import *


class Log_Admin(admin.ModelAdmin):
	list_display = ('id', 'RecordID','TimeOccured', 'NetUser',  'ActionType')
	list_filter = ('ActionType','TableName', 'IsBulk')
	filter_horizontal = ('NetResource_ipsubnets', 'NetResource_dnsexpressions')
	fields = ('TimeOccured',  'NetUser',  'ActionType', 'ValuesBefore', 'ValuesAfter', 'TableName', 'NetResource_ipsubnets', 'NetResource_dnsexpressions', 'RecordID')
	def format_TimeOccured(self, obj):
		return obj.TimeOccured.strftime('%d %b %Y %H:%M')

admin.site.register(log, Log_Admin)

