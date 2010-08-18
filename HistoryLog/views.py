from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from mynet.AccessControl.models import *
from mynet.HistoryLog.models import *
from django.contrib.auth.models import Group, User

import datetime


def LogEvent(action,val_bef, val_aft, is_bulk, uname, gname):
	"""
	This function logs an event  a Record in the database and logs the event in the HistoryLog db. It returns 
	a list of the fields and values that were deleted.
		values: m_id = unique id of record in db, model_name = name of the table in db
	"""
	
	currentNetGroup = Group.objects.get(name = "Network Group")		#netgroup.objects.get(name = ngroup)
	currentUser     = User.objects.get(username__exact = uname)	#usrname.objects.get(uname = user)
	now = datetime.datetime.today()
	newEvent = log( #NetGroupName 		= currentNetGroup,
			NetUser		 	= currentUser,
			TimeOccured		= now,
			ActionType		= action,	
			ValuesBefore		= val_bef,
			ValuesAfter		= val_aft,
			IsBulk 			= is_bulk
		)	
	newEvent.save()
	return 

@login_required
def history(request):
	historyMessage = {'IP': '192.12222.22'}
	#historyLogs = {'TimeOccured':'2010-08-02 09:41:08.720640','ActionType':'EDIT','NetUser':'aaw099','NetGroupName':'NetworkGroup','ValuesBefore':'ip_pair:192.168.0.1','ValuesAfter':'ip_pair:192.168.0.100','TableName':'DNS_names', 'IsBulk':'0' }
	historyLogs = log.objects.all().values()
	#historyMessage["message"] = request.user.message_get.all() try actions
	return render_to_response('qmul_history.html', {'hMessage': historyMessage, 'historyLogs':historyLogs, 'netgroupno':1})
