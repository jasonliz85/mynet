from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout
from mynet.AccessControl import views
admin.autodiscover()

urlpatterns = patterns('',

	#####################################################
	##################General Pages######################
	#####################################################
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jasonl/svn/mynet/media'}),
	('^$', 'mynet.views.home'),
	#('^login/$', 'mynet.views.login'),
	(r'^home/$','mynet.views.home'),
	
	#####################################################
	##################DNS Pages##########################
	#####################################################
	(r'^dns/$', 'mynet.views.dns_page'),
	(r'^dns/namespace$', 'mynet.views.dns_page_addname'),
	
	#####################################################
	##################DHCP Pages#########################
	#####################################################
	(r'^dhcp/$', 'mynet.views.dhcp_page'),					#dhcp - main dchp info page
	(r'^dhcp/registeredmachines$', views.dhcp_page_machine_delete_multiple), #dhcp_page_listings), 	#dhcp - registered machine listings
	
	#CRUD Registered Machine- Create, Read, Update, Destroy
	(r'^dhcp/registermachine$', views.dhcp_page_machine_add),		#dhcp - register a machine
	(r'^dhcp/viewmachine/(\d{1,3})/$', views.dhcp_page_machine_view),	#dhcp - view individual machine
	(r'^dhcp/editmachine/(\d{1,3})/$', views.dhcp_page_machine_edit),	#dhcp - edit an existing machine record
	(r'^dhcp/deletemachine/(\d{1,3})/$', views.dhcp_page_machine_delete_single), 	#dhcp - delete existing machine record (single)
	(r'^dhcp/deletemachine/$', views.dhcp_page_machine_delete_multiple), 	#dhcp - delete existing machine record (multiple)
	(r'^dhcp/viewTest/$', views.dhcp_page_list_machines), 	#dhcp - delete existing machine record (multiple)	
	
	#####################################################
	##################Admin Pages########################
	#####################################################
	(r'^admin/', include(admin.site.urls)),
	(r'^accounts/login/$', login),
	#(r'^login/accounts/login/?next=$', login_redirect),
	(r'^accounts/logout/$', logout),
	
	
	#####################################################
	#####################################################
	#####################################################

	
)
