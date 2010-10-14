from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

	#####################################################
	##################General Pages######################
	#####################################################
urlpatterns = patterns('subnets.views',
	('^$', 'home'),
	#('^login/$', 'subnets.views.login'),
	(r'^home/$','home'),	
	(r'^dns/$', 'dns_page'),						#dns- main dns home page
	(r'^dhcp/$', 'dhcp_page'),						#dhcp - main dchp info page	
	(r'^error/permission/$', 'permission_error'),
	(r'^error/record/$', 'record_error'),
	
)
	#####################################################
	##################Admin Pages########################
	#####################################################
urlpatterns += patterns('django.views.static',	
	#work from qm
	#(r'^site_media/(?P<path>.*)$', 'serve', {'document_root': '/home/jasonl/svn/subnets/Media'}),
	#work from home 
	(r'^site_media/(?P<path>.*)$', 'serve', {'document_root': '/home/jason/Projects/qm_projects/mynet/Media'}),
	#production dungbeetle
	#(r'^site_media/(?P<path>.*)$', 'serve', {'document_root': '/home/django/django_projects/subnets/Media'}),

	(r'^admin/', include(admin.site.urls)),
	(r'^accounts/login/$', login),
	(r'^accounts/logout/$', logout),
)

	#####################################################
	##################History Pages######################
	#####################################################
urlpatterns += patterns('HistoryLog.views',
	
	(r'^history/$','HistoryList'),
	(r'^history/(\d{1,6})/view/single$','HistoryView'),
	(r'^history/(\d{1,6})/view/multiple$', 'HistoryView2'),#'subnets.HistoryLog.views.HistoryView'), #(?P<vtype>\w{8})
	(r'^history/(\d{1,6})/undo/$$','HistoryUndoAction'),
)

	#####################################################
	##################DNS Pages##########################
	#####################################################
urlpatterns += patterns('DNS.views',
		
	#CRUD Registed DNS pairs - Create, Read, Update, Destroy
	(r'^dns/pair/add$', 'dns_namepair_add'),							#dns -
	(r'^dns/pair/list/default$', 'dns_namepair_listing'),				#dns - 
	(r'^dns/pair/(\d{1,6})/view$', 'dns_namepair_view'),				#dns -
	(r'^dns/pair/(\d{1,6})/edit$', 'dns_namepair_edit'),				#dns - 
	(r'^dns/pair/(\d{1,6})/delete$', 'dns_namepair_delete'),			#dns - 
	(r'^dns/add/(\d{1,6})/$', 'dns_namepair_simpleAdd'),

)
	#####################################################
	##################DHCP Pages#########################
	#####################################################
urlpatterns += patterns('DHCP.views',
	
	#CRUD Registered IP Pools- Create, Read, Update, Destroy
	(r'^dhcp/pool/add$', 'dhcp_page_IP_range_add'),						#dhcp - 
	(r'^dhcp/pool/list/$', 'dhcp_page_IP_range_listing'), 				#dhcp - 
	(r'^dhcp/pool/list/default$', 'dhcp_page_IP_range_listing'), 		#dhcp - 
	(r'^dhcp/pool/(\d{1,6})/view$', 'dhcp_page_IP_range_view'),			#dhcp - 
	(r'^dhcp/pool/(\d{1,6})/edit$', 'dhcp_page_IP_range_edit'),			#dhcp - 
	(r'^dhcp/pool/(\d{1,6})/delete$', 'dhcp_page_IP_range_delete'), 	#dhcp - 
	
	#CRUD Registered Machfrom django.conf.urls.defaults import *ine- Create, Read, Update, Destroy
	(r'^dhcp/machine/add$', 'dhcp_page_machine_add'),							#dhcp - register a machine
	#url(r'^dhcp/machine/list/default/', 'dhcp_page_machine_listing'), 			#dhcp - registered machine listings
	#?ot=asc&amp;o=1
	(r'^dhcp/machine/list/$', 'dhcp_page_machine_listing'),						#dhcp - registered machine listings
	#(r'^dhcp/machine/list/(?P<page_index>\d+)/$', 'dhcp_page_machine_listing'), #dhcp - registered machine listings, x pages per record
	(r'^dhcp/machine/(\d{1,6})/view$', 'dhcp_page_machine_view'),				#dhcp - view individual machine
	(r'^dhcp/machine/(\d{1,6})/edit$', 'dhcp_page_machine_edit'),				#dhcp - edit an existing machine record
	(r'^dhcp/machine/(\d{1,6})/delete$', 'dhcp_page_machine_delete_single'), 	#dhcp - delete existing machine record (single)
	#(r'^dhcp/machine/list/(?P<sort_by>[a-z])/(?P<page_index>\d+)/$', 'dhcp_page_machine_listing' ), 		
	#(r'^dhcp/deletemachine/$', views.dhcp_page_machine_delete_multiple), 		#dhcp - delete existing machine record (multiple)
	#(r'^dhcp/viewTest/$', views.dhcp_page_list_machines), 				#dhcp - delete existing machine record (multiple)	
	
)


