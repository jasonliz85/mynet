from django import forms
from IPy import IP
from netaddr import *

class RegisterMachineForm(forms.Form):
	mcID = forms.CharField(max_length=40, min_length=5, label = 'MAC Address')
	ipID = forms.CharField(label = 'IP Address', max_length = 40 )
	pcID = forms.CharField(max_length=15, label = 'PC Name')
	dscr = forms.CharField(required=False, widget = forms.Textarea, label = 'Description')
	def clean_ipID(self):
		ipID = self.cleaned_data['ipID']
		try: 
			IPAddress(ipID)
	   	except (NameError, TypeError, AddrFormatError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	except ValueError:
	   		raise forms.ValidationError("Netmasks or subnet prefixes are not allowed. ")
	   	return ipID
	def clean_mcID(self):
		mcID = self.cleaned_data['mcID']
		try:
			EUI(mcID)
		except (NameError, AddrFormatError):
			raise forms.ValidationError("MAC address is not valid. Please change and try again.")		
		return mcID
		
class Register_IP_range_Form(forms.Form):									
	IP_range1	= forms.CharField(label = 'Address Range', max_length = 40 )					
	IP_range2	= forms.CharField(label = 'Range To', max_length = 40 )
	dscr 		= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')

	def clean_IP_range1(self):
		IP_range1 = self.cleaned_data['IP_range1']
		try: 
			IPAddress(IP_range1)
   	   	except (NameError, TypeError, AddrFormatError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	except ValueError:
	   		raise forms.ValidationError("Netmasks or subnet prefixes are not allowed. ")
	   	return IP_range1
		
	def clean_IP_range2(self):
		IP_range2 = self.cleaned_data['IP_range2']
		try: 
			IPAddress(IP_range2)
   	   	except (NameError, TypeError, AddrFormatError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	except ValueError:
	   		raise forms.ValidationError("Netmasks or subnet prefixes are not allowed. ")
	   	return IP_range2
	   	 
	#to check:
	#	-IP version consistent
	#	-single ip values and not a range
	#
class Register_namepair_Form(forms.Form):
	dns_expr 	= forms.CharField(label = 'Machine Name', widget = forms.TextInput(attrs={'class':'special', 'size':'10'}))		#DNS name regular expression
	ip_pair		= forms.CharField(label = 'IP Address', widget = forms.TextInput(attrs={'class':'special'}))					
	TYPE_CHOICES = ( 
			('1BD', 'Bi-Directional '), 			# 
	                ('2NA', 'Machine Name --> IP Address'), 		# NA = name-address
        	        ('3AN', 'Machine Name <-- IP Address'), 	# AD = address-name
			)
	dns_typ		= forms.ChoiceField(choices=TYPE_CHOICES, initial = '1BD', widget = forms.RadioSelect(), label = 'Type')
	dscr 		= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')
	
	def clean_ip_pair(self):
		ip_pair = self.cleaned_data['ip_pair']
		try: 
			IP(ip_pair)
	   	except (ValueError, NameError, TypeError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
   		if IP(ip_pair).len() > 1:
	   		raise forms.ValidationError("Please enter a single IP address, not a range. ")
	   	return ip_pair
class Register_service_Form(forms.Form):
	service_name 	= forms.CharField(label = 'Machine Name', widget = forms.TextInput(attrs={'class':'special', 'size':'10'}))		#DNS name regular expression
	dscr 		= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')

class ViewMachinesActionForm(forms.Form):
	STATUS_CHOICES = ( 
			('act', ''),
	                ('del', 'Delete Selected'),
        	        ('vue', 'View Selected'),
			)
	status = forms.ChoiceField(choices=STATUS_CHOICES, initial='act')
	cbox_id = forms.BooleanField(required=False)	
	#need to somehow implement this check
	def clean_data(self):
		cbox_id = self.cleaned_data['cbox_id']
		if not cbox_id:
			raise forms.ValidationError("Please select at least one item.")
		elif status == 'act':
			raise forms.ValidationError("Please select at least one action")
		return 


		
