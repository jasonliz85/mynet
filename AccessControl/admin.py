from django.contrib import admin
from mynet.AccessControl.models import * # DHCP_machine, test_machine, DHCP_ip_pool, DNS_names, DNS_ipval, DNS_expr

from mynet.AccessControl.models import NetGroup

class NetGroup_Admin(admin.ModelAdmin):
	filter_horizontal = ('address_blocks', 'dns_patterns', 'managed_by')
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')

admin.site.register(NetGroup, NetGroup_Admin)
admin.site.register(DNS_expr)
admin.site.register(DNS_ipval)

