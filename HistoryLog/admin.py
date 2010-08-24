from django.contrib import admin
from mynet.HistoryLog.models import *


class Log_Admin(admin.ModelAdmin):
	list_display = ('TimeOccured', 'NetUser',  'ActionType')
	fields = ('TimeOccured',  'NetUser',  'ActionType', 'ValuesBefore', 'ValuesAfter', 'TableName')
	def format_TimeOccured(self, obj):
		return obj.TimeOccured.strftime('%d %b %Y %H:%M')

#class NetGroup_Admin(admin.ModelAdmin):
#	list_display = ('id', 'name')
	
#class Usrname_Admin(admin.ModelAdmin):
#	list_display = ('id', 'uname',)

admin.site.register(log, Log_Admin)
#admin.site.register(netgroup, NetGroup_Admin)
#admin.site.register(usrname, Usrname_Admin)

