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
	rmID = forms.IntegerField()
	mcID = forms.CharField(max_length=12, min_length=5, label = 'MAC Address')
	ipID = forms.IPAddressField(label = 'IP Address')
	pcID = forms.CharField(max_length=15, label = 'PC Name')
	dscr = forms.CharField(required=False, widget = forms.Textarea, label = 'Description')

