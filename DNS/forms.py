from django import forms
from netaddr import *
from string import replace, lstrip, rstrip

class Register_namepair_Form(forms.Form):
	dns_expr 	= forms.CharField(label = 'Machine Name', widget = forms.TextInput(attrs={'class':'special', 'size':'10'}))		#DNS name regular expression
	ip_address	= forms.CharField(label = 'IP Address', max_length = 40 )#widget = forms.TextInput(attrs={'class':'special'}))					
	TYPE_CHOICES = ( 
					('1BD', 'Bi-Directional '), 				# BD = bi-directional 
	                ('2NA', 'Machine Name --> IP Address'), 	# NA = name-address
        	        ('3AN', 'IP Address --> Machine Name'), 	# AD = address-name
			)
	dns_type	= forms.ChoiceField(choices=TYPE_CHOICES, initial = '1BD', widget = forms.RadioSelect(), label = 'Type')
	dscr 		= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')
	ttl			= forms.IntegerField(label = 'Time to Live', initial= 0)
	def clean_ip_address(self):
		ip_address = self.cleaned_data['ip_address']
		ip_address = ip_address.replace(' ','')
		try: 
			ip_addr = IPAddress(ip_address)
   		except (NameError, TypeError, AddrFormatError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	except ValueError:
	   		raise forms.ValidationError("Netmasks or subnet prefixes are not allowed. ")
	   	return ip_address
	def clean_dns_expr(self):
		dns_expr = self.cleaned_data['dns_expr']		
		dns_expr = dns_expr.replace(' ','')
		return dns_expr
	def clean_dscr(self):
		dscr = self.cleaned_data['dscr']
		dscr = dscr.lstrip()
		dscr = dscr.rstrip()
		return dscr
#	def clean_ttl(self):
#		try:
#			ttl_cleaned = int(self.cleaned_data['ttl_cleaned'])
#		except :
#			raise forms.ValidationError("This time to live value is incorrect, need to be an integer in seconds.")
#		return ttl_cleaned
		
class Register_service_Form(forms.Form):
	service_name 	= forms.CharField(label = 'Machine Name', widget = forms.TextInput(attrs={'class':'special', 'size':'10'}))		#DNS name regular expression
	dscr 			= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')
	ttl				= forms.IntegerField(required = False,label = 'Time to Live (seconds)', initial= 0)
	def clean_service_name(self):
		service_name = self.cleaned_data['service_name']		
		service_name = service_name.replace(' ','')
		return service_name
#	def clean_ttl(self):
#		try:
#			ttl_cleaned = int(self.cleaned_data['ttl_cleaned'])
#		except:
#			raise forms.ValidationError("This time to live value is incorrect, needs to be an integer (in seconds).")
#		return ttl_cleaned
		
class ViewMachinesActionForm(forms.Form):
	STATUS_CHOICES = ( 
					('act', ''),
	                ('del', 'Delete Selected'),
        	        ('vue', 'View Selected'),
			)
	status = forms.ChoiceField(choices=STATUS_CHOICES, initial='act')
	cbox_id = forms.BooleanField(required=False)	
	def clean_data(self):
		cbox_id = self.cleaned_data['cbox_id']
		if not cbox_id:
			raise forms.ValidationError("Please select at least one item.")
		elif status == 'act':
			raise forms.ValidationError("Please select at least one action")
		return 

class UploadFileForm(forms.Form):
    file  = forms.FileField()


