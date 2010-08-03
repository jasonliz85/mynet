from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from mynet.AccessControl.models import *
from mynet.HistoryLog.models import *

@login_required
def history(request):
	historyMessage = {'IP': '192.12222.22'}
	#historyLogs = {'TimeOccured':'2010-08-02 09:41:08.720640','ActionType':'EDIT','NetUser':'aaw099','NetGroupName':'NetworkGroup','ValuesBefore':'ip_pair:192.168.0.1','ValuesAfter':'ip_pair:192.168.0.100','TableName':'DNS_names', 'IsBulk':'0' }
	historyLogs = log.objects.all().values()
	#historyMessage["message"] = request.user.message_get.all() try actions
	return render_to_response('qmul_history.html', {'hMessage': historyMessage, 'historyLogs':historyLogs, 'netgroupno':1})
