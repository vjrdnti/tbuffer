from django import forms

class EncryptForm(forms.Form):
    image      = forms.ImageField()
    secret_key = forms.CharField(max_length=256)

class DecryptForm(forms.Form):
    image = forms.ImageField()
    secret_key = forms.CharField(
        max_length=256,
        label="Secret Key",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your secret key'})
    )
    key_file   = forms.FileField()  #for da composite string
