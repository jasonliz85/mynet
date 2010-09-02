from django import forms
from netaddr import *

class Register_namepair_Form(forms.Form):
	dns_expr 	= forms.CharField(label = 'Machine Name', widget = forms.TextInput(attrs={'class':'special', 'size':'10'}))		#DNS name regular expression
	ip_pair		= forms.CharField(label = 'IP Address', max_length = 40 )#widget = forms.TextInput(attrs={'class':'special'}))					
	TYPE_CHOICES = ( 
			('1BD', 'Bi-Directional '), 			# BD = bi-directional
	                ('2NA', 'Machine Name --> IP Address'), 	# NA = name-address
        	        ('3AN', 'IP Address --> Machine Name'), 	# AD = address-name
			)
	dns_typ		= forms.ChoiceField(choices=TYPE_CHOICES, initial = '1BD', widget = forms.RadioSelect(), label = 'Type')
	dscr 		= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')
	
	def clean_ip_pair(self):
		ip_pair = self.cleaned_data['ip_pair']
		try: 
			ip_addr = IPAddress(ip_pair)
   		except (NameError, TypeError, AddrFormatError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	except ValueError:
	   		raise forms.ValidationError("Netmasks or subnet prefixes are not allowed. ")

	   	return ip_pair
