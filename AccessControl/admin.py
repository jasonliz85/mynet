from django.contrib import admin
from mynet.AccessControl.models import * # DHCP_machine, test_machine, DHCP_ip_pool, DNS_names, DNS_ipval, DNS_expr

from mynet.AccessControl.models import NetGroup


class DHCP_Mach_Admin(admin.ModelAdmin):
	list_display = ('id','MAC_pair', 'IP_pair', 'PC_pair')
	fields = ('MAC_pair', 'IP_pair', 'PC_pair', 'description')
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')

class DHCP_Pool_Admin(admin.ModelAdmin):
	list_display = ('id','IP_pool1', 'IP_pool2')
	fields = ('IP_pool1', 'IP_pool2', 'description' )
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')

class DNS_Admin(admin.ModelAdmin):
	list_display = ('id','machine_name', 'ip_pair', 'dns_type')
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')

class NetGroup_Admin(admin.ModelAdmin):
	filter_horizontal = ('address_blocks', 'dns_patterns', 'managed_by')
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')

	

admin.site.register(DHCP_machine, DHCP_Mach_Admin)
admin.site.register(DHCP_ip_pool, DHCP_Pool_Admin )
admin.site.register(DNS_names, DNS_Admin)

admin.site.register(NetGroup, NetGroup_Admin)
admin.site.register(DNS_expr)
admin.site.register(DNS_ipval)

