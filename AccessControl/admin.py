from django.contrib import admin
from subnets.AccessControl.models import * # DHCP_machine, test_machine, DHCP_ip_pool, DNS_names, DNS_ipval, DNS_expr

from subnets.AccessControl.models import NetGroup

class NetGroup_Admin(admin.ModelAdmin):
	list_display = ('id', 'name')
	filter_horizontal = ('address_blocks', 'dns_patterns', 'managed_by')
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')
class subnet_Admin(admin.ModelAdmin):
	list_display = ('id', 'ip_network', 'vlan')
	fields = ('ip_network', 'vlan', 'description')
class dns_Admin(admin.ModelAdmin):
	list_display = ('id', 'expression')

admin.site.register(NetGroup, NetGroup_Admin)
admin.site.register(dns_expression, dns_Admin)
admin.site.register(ip_subnet, subnet_Admin)

