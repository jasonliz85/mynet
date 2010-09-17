from django import forms
from netaddr import *

class RegisterMachineForm(forms.Form):
	mcID = forms.CharField(max_length=40, min_length=5, label = 'MAC Address')
	ipID = forms.CharField(label = 'IP Address', max_length = 40 )
	pcID = forms.CharField(max_length=15, label = 'Host Name')
	dscr = forms.CharField(required=False, widget = forms.Textarea, label = 'Description')
	def clean_ipID(self):
		ipID = self.cleaned_data['ipID']
		ipID = ipID.replace(' ','')
		try: 
			IPAddress(ipID)
	   	except (NameError, TypeError, AddrFormatError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	except ValueError:
	   		raise forms.ValidationError("Netmasks or subnet prefixes are not allowed. ")
	   	return ipID
	def clean_mcID(self):
		mcID = self.cleaned_data['mcID']
		mcID = mcID.replace(' ','')
		try:
			EUI(mcID)
		except (NameError, AddrFormatError):
			raise forms.ValidationError("MAC address is not valid. Please change and try again.")			
		return mcID
	def clean_dscr(self):
		dscr = self.cleaned_data['dscr']
		dscr = dscr.lstrip()
		dscr = dscr.rstrip()
		return dscr
		
class Register_IP_range_Form(forms.Form):									
	IP_range1	= forms.CharField(label = 'Address Range', max_length = 40 )					
	IP_range2	= forms.CharField(label = 'Range To', max_length = 40 )
	dscr 		= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')

	def clean_IP_range1(self):
		IP_range1 = self.cleaned_data['IP_range1']
		IP_range1 = IP_range1.replace(' ','')
		try: 
			IPAddress(IP_range1)
		except (NameError, TypeError, AddrFormatError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	except ValueError:
	   		raise forms.ValidationError("Netmasks or subnet prefixes are not allowed. ")
	   	return IP_range1
		
	def clean_IP_range2(self):
		IP_range2 = self.cleaned_data['IP_range2']
		IP_range2 = IP_range2.replace(' ','')
		try: 
			IPAddress(IP_range2)
   	   	except (NameError, TypeError, AddrFormatError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	except ValueError:
	   		raise forms.ValidationError("Netmasks or subnet prefixes are not allowed. ")
	   	return IP_range2
	def clean_dscr(self):
		dscr = self.cleaned_data['dscr']
		dscr = dscr.lstrip()
		dscr = dscr.rstrip()
		return dscr
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
   	 

