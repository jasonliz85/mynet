from django.contrib import admin
from subnets.HistoryLog.models import *


class Log_Admin(admin.ModelAdmin):
	list_display = ('id', 'RecordID','TimeOccured', 'NetUser',  'ActionType')
	list_filter = ('ActionType','TableName', 'IsBulk')
	fields = ('TimeOccured',  'NetUser',  'ActionType', 'ValuesBefore', 'ValuesAfter', 'TableName', 'RecordID')
	def format_TimeOccured(self, obj):
		return obj.TimeOccured.strftime('%d %b %Y %H:%M')

admin.site.register(log, Log_Admin)

