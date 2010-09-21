from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

	#####################################################
	##################General Pages######################
	#####################################################
urlpatterns = patterns('mynet.views',
	('^$', 'home'),
	#('^login/$', 'mynet.views.login'),
	(r'^home/$','home'),	
	(r'^dns/$', 'dns_page'),						#dns- main dns home page
	(r'^dhcp/$', 'dhcp_page'),						#dhcp - main dchp info page
	
)
	#####################################################
	##################Admin Pages########################
	#####################################################
urlpatterns += patterns('django.views.static',	
	#work from qm
	(r'^site_media/(?P<path>.*)$', 'serve', {'document_root': '/home/jasonl/svn/mynet/Media'}),
	#work from home
	#(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/jason/Projects/qm_projects/mynet/media'}),
	(r'^admin/', include(admin.site.urls)),
	(r'^accounts/login/$', login),
	(r'^accounts/logout/$', logout),
)

	#####################################################
	##################History Pages######################
	#####################################################
urlpatterns += patterns('HistoryLog.views',
	
	(r'^history/$','HistoryList'),
	(r'^history/(\d{1,3})/view/single$','HistoryView'),
	(r'^history/(\d{1,3})/view/multiple$', 'HistoryView2'),#'mynet.HistoryLog.views.HistoryView'), #(?P<vtype>\w{8})
	(r'^history/(\d{1,3})/undo/$$','HistoryUndoAction'),
)

	#####################################################
	##################DNS Pages##########################
	#####################################################
urlpatterns += patterns('DNS.views',
		
	#CRUD Registed DNS pairs - Create, Read, Update, Destroy
#	(r'^dns/register_DNS_pair$', 'dns_namepair_add'),				#dns -
#	(r'^dns/view_DNS_pair/(\d{1,3})/$', 'dns_namepair_view'),			#dns -
#	(r'^dns/registered_DNS_pairs$', 'dns_namepair_listing'),			#dns - 
#	(r'^dns/edit_DNS_pair/(\d{1,3})/$', 'dns_namepair_edit'),			#dns - 
#	(r'^dns/delete_DNS_pair/(\d{1,3})/$', 'dns_namepair_delete'),			#dns - 
#	(r'^dns/add/(\d{1,3})/$', 'dns_namepair_simpleAdd'),
	(r'^dns/pair/add$', 'dns_namepair_add'),					#dns -
	(r'^dns/pair/list/default$', 'dns_namepair_listing'),				#dns - 
	(r'^dns/pair/(\d{1,3})/view$', 'dns_namepair_view'),				#dns -
	(r'^dns/pair/(\d{1,3})/edit$', 'dns_namepair_edit'),				#dns - 
	(r'^dns/pair/(\d{1,3})/delete$', 'dns_namepair_delete'),			#dns - 
	(r'^dns/add/(\d{1,3})/$', 'dns_namepair_simpleAdd'),

)
	#####################################################
	##################DHCP Pages#########################
	#####################################################
urlpatterns += patterns('DHCP.views',
	
	#CRUD Registered IP Pools- Create, Read, Update, Destroy
#	(r'^dhcp/register_IP_range/$', 'dhcp_page_IP_range_add'),			#dhcp - 
#	(r'^dhcp/view_IP_range/(\d{1,3})/$', 'dhcp_page_IP_range_view'),		#dhcp - 
#	(r'^dhcp/registered_IP_pools$', 'dhcp_page_IP_range_listing'), 			#dhcp - 
#	(r'^dhcp/edit_IP_range/(\d{1,3})/$', 'dhcp_page_IP_range_edit'),		#dhcp - 
#	(r'^dhcp/delete_IP_range/(\d{1,3})/$', 'dhcp_page_IP_range_delete'), 		#dhcp - 
	(r'^dhcp/pool/add$', 'dhcp_page_IP_range_add'),					#dhcp - 
	(r'^dhcp/pool/list/default$', 'dhcp_page_IP_range_listing'), 			#dhcp - 
	(r'^dhcp/pool/(\d{1,3})/view$', 'dhcp_page_IP_range_view'),			#dhcp - 
	(r'^dhcp/pool/(\d{1,3})/edit$', 'dhcp_page_IP_range_edit'),			#dhcp - 
	(r'^dhcp/pool/(\d{1,3})/delete$', 'dhcp_page_IP_range_delete'), 		#dhcp - 
	
	#CRUD Registered Machine- Create, Read, Update, Destroy
#	(r'^dhcp/registermachine/$', 'dhcp_page_machine_add'),				#dhcp - register a machine
#	(r'^dhcp/viewmachine/(\d{1,3})/$', 'dhcp_page_machine_view'),			#dhcp - view individual machine
#	(r'^dhcp/registeredmachines$', 'dhcp_page_machine_delete_multiple'), 		#dhcp_page_listings), 	#dhcp - registered machine listings
#	(r'^dhcp/editmachine/(\d{1,3})/$', 'dhcp_page_machine_edit'),			#dhcp - edit an existing machine record
#	(r'^dhcp/deletemachine/(\d{1,3})/$', 'dhcp_page_machine_delete_single'), 	#dhcp - delete existing machine record (single)
	(r'^dhcp/machine/add$', 'dhcp_page_machine_add'),				#dhcp - register a machine
	(r'^dhcp/machine/list/default$', 'dhcp_page_machine_delete_multiple'), 		#dhcp_page_listings), 	#dhcp - registered machine listings
	(r'^dhcp/machine/(\d{1,3})/view$', 'dhcp_page_machine_view'),			#dhcp - view individual machine
	(r'^dhcp/machine/(\d{1,3})/edit$', 'dhcp_page_machine_edit'),			#dhcp - edit an existing machine record
	(r'^dhcp/machine/(\d{1,3})/delete$', 'dhcp_page_machine_delete_single'), 	#dhcp - delete existing machine record (single)
	
	#(r'^dhcp/deletemachine/$', views.dhcp_page_machine_delete_multiple), 		#dhcp - delete existing machine record (multiple)
	#(r'^dhcp/viewTest/$', views.dhcp_page_list_machines), 				#dhcp - delete existing machine record (multiple)	
	
)


