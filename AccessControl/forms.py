from django import forms

class RegisterMachineForm(forms.Form):
	mcID = forms.CharField(max_length=12, min_length=5, label = 'MAC Address')
	ipID = forms.IPAddressField(label = 'IP Address')
	pcID = forms.CharField(max_length=15, label = 'PC Name')
	dscr = forms.CharField(required=False, widget = forms.Textarea, label = 'Description')
	
	#def clean_message(self):
	#	message = self.cleaned_data['message']
	#	num_words = len(message.split())
	#	if num_words < 4:
	#   		raise forms.ValidationError("Not enough words!")
	#	return message

class EditRegisteredMachineForm(forms.Form):
	mcID = forms.CharField(max_length=12, min_length=5, label = 'MAC Address')
	ipID = forms.IPAddressField(label = 'IP Address')
	pcID = forms.CharField(max_length=15, label = 'PC Name')
	dscr = forms.CharField(required=False, widget = forms.Textarea, label = 'Description')
	
class ViewMachinesForm(forms.Form):
	mcID = forms.CharField(label = 'MAC Address')
	ipID = forms.IPAddressField(label = 'IP Address')
	pcID = forms.CharField(label = 'PC Name')
	date_created = forms.DateTimeField(label = 'Date Created')
	#date_deleted = forms.DateTimeField(label = 'Date Deleted')
	#description = forms.CharField(label = 'Description')
			
class ViewMachinesActionForm(forms.Form):
	STATUS_CHOICES = ( 
			('act', ''),
	                ('del', 'Delete Selected'),
        	        ('vue', 'View Selected'),
			)
	status = forms.ChoiceField(choices=STATUS_CHOICES, initial='act')
	cbox_id = forms.BooleanField(required=False)
	
class DeleteRegisteredMachineForm(forms.Form):
	STATUS_CHOICES = ( 
			('act', ''),
	                ('del', 'Delete Selected'),
        	        ('vue', 'View Selected'),
			)
	status = forms.ChoiceField(choices=STATUS_CHOICES, initial='act')
	cbox_id = forms.BooleanField(required=False)
	#m_value =  forms.IntegerField()
	#machine_ID = forms.IntegerField()
	#mcID = forms.CharField(max_length=12, min_length=5, label = 'MAC Address')
	#ipID = forms.IPAddressField(label = 'IP Address')
	
