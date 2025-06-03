from django import forms

class ActivityDeadlineForm(forms.Form):
    activity_id = forms.CharField(widget=forms.HiddenInput())
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'w-full bg-blue-500/50 text-white p-4 rounded-2xl border border-blue-400 cursor-not-allowed'}))
    description = forms.CharField(label="Description", widget=forms.Textarea(attrs={'readonly': 'readonly', 'class': 'w-full bg-blue-500/50 text-white p-4 rounded-2xl border border-blue-400 cursor-not-allowed'}))
    date = forms.DateField(label="Set Date", widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full bg-blue-700 text-white p-4 rounded-2xl border border-blue-800'}))
    time = forms.TimeField(label="Set Time", widget=forms.TimeInput(attrs={'type': 'time', 'class': 'w-full bg-blue-700 text-white p-4 rounded-2xl border border-blue-800'}))