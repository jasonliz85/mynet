from django import forms
from netaddr import *

class Register_namepair_Form(forms.Form):
	dns_expr 	= forms.CharField(label = 'Machine Name', widget = forms.TextInput(attrs={'class':'special', 'size':'10'}))		#DNS name regular expression
	ip_address	= forms.CharField(label = 'IP Address', max_length = 40 )#widget = forms.TextInput(attrs={'class':'special'}))					
	TYPE_CHOICES = ( 
			('1BD', 'Bi-Directional '), 			# 
	                ('2NA', 'Machine Name --> IP Address'), 		# NA = name-address
        	        ('3AN', 'IP Address --> Machine Name'), 	# AD = address-name
			)
	dns_typ		= forms.ChoiceField(choices=TYPE_CHOICES, initial = '1BD', widget = forms.RadioSelect(), label = 'Type')
	dscr 		= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')
	
	def clean_ip_address(self):
		ip_address = self.cleaned_data['ip_address']
		try: 
			ip_addr = IPAddress(ip_address)
   		except (NameError, TypeError, AddrFormatError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	except ValueError:
	   		raise forms.ValidationError("Netmasks or subnet prefixes are not allowed. ")

	   	return ip_address
	   	
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

