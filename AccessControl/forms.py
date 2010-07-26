from django import forms
from IPy import IP

class RegisterMachineForm(forms.Form):
	mcID = forms.CharField(max_length=12, min_length=5, label = 'MAC Address')
	ipID = forms.CharField(label = 'IP Address', max_length = 40 )
	pcID = forms.CharField(max_length=15, label = 'PC Name')
	dscr = forms.CharField(required=False, widget = forms.Textarea, label = 'Description')
	#TO DO: basic validation checks
	#checks on ip address
	#checks on mac address
	def clean_ipID(self):
		ipID = self.cleaned_data['ipID']
		try: 
			IP(ipID)
	   	except (ValueError, NameError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
	   	
	   	if IP(ipID).len() > 1:
	   		raise forms.ValidationError("Please enter a single IP address, not a range. ")
	   	
	   	return ipID

class Register_IP_range_Form(forms.Form):									
	IP_range1	= forms.CharField(label = 'Address Range', max_length = 40 )					
	IP_range2	= forms.CharField(label = 'Range To', max_length = 40 )
	dscr 		= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')

	def clean_IP_range1(self):
		IP_range1 = self.cleaned_data['IP_range1']
		try: 
			IP(IP_range1)
	   	except (ValueError, NameError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
   		if IP(IP_range1).len() > 1:
	   		raise forms.ValidationError("Please enter a single IP address, not a range. ")
	   	return IP_range1
		
	def clean_IP_range2(self):
		IP_range2 = self.cleaned_data['IP_range2']
		try: 
			IP(IP_range2)
	   	except (ValueError, NameError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
   		if IP(IP_range2).len() > 1:
	   		raise forms.ValidationError("Please enter a single IP address, not a range. ")
	   	return IP_range2
	   	 
	#to check:
	#	-IP version consistent
	#	-single ip values and not a range
	#
class Register_namepair_Form(forms.Form):
	dns_expr 	= forms.CharField(label = 'DNS Expression', max_length = 30)		#DNS name regular expression
	ip_pair		= forms.CharField(label = 'IP Address', max_length = 40 )					
	dscr 		= forms.CharField(required = False, widget = forms.Textarea, label = 'Description')
	
	def clean_ip_pair(self):
		ip_pair = self.cleaned_data['ip_pair']
		try: 
			IP(ip_pair)
	   	except (ValueError, NameError): 
	   		raise forms.ValidationError("IP address is not valid. Please change and try again. ")
   		if IP(ip_pair).len() > 1:
	   		raise forms.ValidationError("Please enter a single IP address, not a range. ")
	   	return ip_pair
	   	
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


		
