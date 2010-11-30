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
	(r'^importexport/$','importexport_main'),
	(r'^information/$','information_main'),
	(r'^temp/info$','time_info'),
)
urlpatterns += patterns('AccessControl.views',
	(r'^subnets/get-subnet-data$', 'subnets_fetch_records_txt'),
)
	#####################################################
	##################Admin Pages########################
	#####################################################
urlpatterns += patterns('django.views.static',	
	(r'^admin/', include(admin.site.urls)),
	(r'^accounts/login/$', login),
	(r'^accounts/logout/$', logout),
	#work from dungbeetle
	#(r'^site_media/(?P<path>.*)$', 'serve', {'document_root': '/home/django/django_projects/subnets/Media'}),
	#work from qm
	(r'^site_media/(?P<path>.*)$', 'serve', {'document_root': '/home/jasonl/svn/subnets/Media'}),
	 #work from home ##django.views.static
	#(r'^site_media/(?P<path>.*)$', 'serve', {'document_root': '/home/jason/Projects/qm_projects/subnets/Media'}),
)

	#####################################################
	##################History Pages######################
	#####################################################
urlpatterns += patterns('HistoryLog.views',
	#view pages for the HistoryLog APP
	(r'^history/$','HistoryList'),
	(r'^history/(\d{1,6})/view/', 'HistoryView'),
	(r'^history/(\d{1,6})/undo/$$','HistoryUndoAction'),
)

	#####################################################
	##################DNS Pages##########################
	#####################################################
urlpatterns += patterns('DNS',
	#Fetch all DNS records formatted for tiny-dns	
	(r'dns/get-dns-data-txt','views.dns_fetch_records_txt'),
	(r'dns/get-dns-data','views.dns_fetch_records_txt'),
		
	#CRUD Registed DNS pairs - Create, Read, Update, Destroy
	(r'^dns/pair/add$', 'views.dns_namepair_add'),							#dns -
	(r'^dns/pair/list/$', 'views.dns_namepair_listing'),					#dns - 
	(r'^dns/pair/list/default$', 'views.dns_namepair_listing'),				#dns - 
	(r'^dns/pair/(\d{1,6})/view$', 'views.dns_namepair_view'),				#dns -
	(r'^dns/pair/(\d{1,6})/edit$', 'views.dns_namepair_edit'),				#dns - 
	(r'^dns/pair/(\d{1,6})/delete$', 'views.dns_namepair_delete'),			#dns - 
	(r'^dns/add/(\d{1,6})/$', 'views.dns_namepair_simpleAdd'),
	(r'^dns/import$', 'import.import_dns'),
	(r'^dns/export$', 'export.export_dns'),
)
	#####################################################
	##################DHCP Pages#########################
	#####################################################
urlpatterns += patterns('DHCP',
	#Fetch all DHCP details belong to a subnet for dhcpd
	('dhcp/get-pool-data$','views.dhcp_fetch_pool_data'),
	('dhcp/get-host-data$','views.dhcp_fetch_host_data'),
	(r'^dhcp/import$', 'import.import_dhcp'),
	(r'^dhcp/export$', 'export.export_dhcp'),
	#CRUD Registered IP Pools- Create, Read, Update, Destroy
	(r'^dhcp/pool/add$', 'views.dhcp_page_IP_range_add'),						#dhcp - 
	(r'^dhcp/pool/list/$', 'views.dhcp_page_IP_range_listing'), 				#dhcp - 
	(r'^dhcp/pool/list/default$', 'views.dhcp_page_IP_range_listing'), 		#dhcp - 
	(r'^dhcp/pool/(\d{1,6})/view$', 'views.dhcp_page_IP_range_view'),			#dhcp - 
	(r'^dhcp/pool/(\d{1,6})/edit$', 'views.dhcp_page_IP_range_edit'),			#dhcp - 
	(r'^dhcp/pool/(\d{1,6})/delete$', 'views.dhcp_page_IP_range_delete'), 	#dhcp - 
	
	#CRUD Registered Machfrom django.conf.urls.defaults import *ine- Create, Read, Update, Destroy
	(r'^dhcp/machine/add$', 'views.dhcp_page_machine_add'),							#dhcp - register a machine
	(r'^dhcp/machine/list/$', 'views.dhcp_page_machine_listing'),						#dhcp - registered machine listings
	(r'^dhcp/machine/(\d{1,6})/view$', 'views.dhcp_page_machine_view'),				#dhcp - view individual machine
	(r'^dhcp/machine/(\d{1,6})/edit$', 'views.dhcp_page_machine_edit'),				#dhcp - edit an existing machine record
	(r'^dhcp/machine/(\d{1,6})/delete$', 'views.dhcp_page_machine_delete_single'), 	#dhcp - delete existing machine record (single)
	
)


