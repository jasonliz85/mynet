from django.contrib import admin
from subnets.DHCP.models import *
from subnets.NetaddrCustomizations.models import *

class DHCP_Mach_Admin(admin.ModelAdmin):
	list_display = ('id','mac_address', 'ip_address', 'host_name')
	fields = ('mac_address', 'ip_address', 'host_name', 'description', 'is_ipv6', 'time_created', 'time_modified')
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')

class DHCP_Pool_Admin(admin.ModelAdmin):
	list_display = ('id','ip_first', 'ip_last')
	fields = ('ip_first', 'ip_last', 'description', 'is_ipv6', 'time_created', 'time_modified' )
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')
		
		
admin.site.register(DHCP_machine, DHCP_Mach_Admin)
admin.site.register(DHCP_ip_pool, DHCP_Pool_Admin )
