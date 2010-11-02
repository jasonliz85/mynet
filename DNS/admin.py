from django.contrib import admin
from subnets.DNS.models import *

class DNS_Admin(admin.ModelAdmin):
	list_display = ('id','name', 'ip_address', 'dns_type', 'ttl')
	list_filter = ('is_ipv6',)
	fields = ('name', 'ip_address', 'dns_type', 'ttl', 'description', 'is_ipv6', 'time_created', 'time_modified')
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')
		
admin.site.register(DNS_name, DNS_Admin)
