from django.contrib import admin
from mynet.DNS.models import *

class DNS_Admin(admin.ModelAdmin):
	list_display = ('id','name', 'ip_address', 'dns_type')
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')
		
admin.site.register(DNS_name, DNS_Admin)
