from django import forms


class StringForm(forms.Form):
    string = forms.CharField(
        widget=forms.TextInput())
