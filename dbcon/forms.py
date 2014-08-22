from django import forms

class DaterForm(forms.Form):
    start_date = forms.CharField(max_length=40, value='Start', required=True)
    end_date = forms.CharField(max_length=40, required=True)
