from django.contrib import admin
from mynet.AccessControl.models import DHCP_machine, test_machine, DHCP_ip_pool, DNS_names


class DHCP_Admin(admin.ModelAdmin):
	list_display = ('MAC_pair', 'IP_pair', 'PC_pair', 'time_created')
	fields = ('MAC_pair', 'IP_pair', 'PC_pair', 'description' ,'time_created','time_deleted')
	def format_date(self, obj):
		return obj.date.strftime('%d %b %Y %H:%M')
#	format_date.short_description = 'Date'


admin.site.register(DHCP_machine, DHCP_Admin)
admin.site.register(DNS_names)
admin.site.register(test_machine)
admin.site.register(DHCP_ip_pool)

