from django import forms


class Form1(forms.Form):
    text = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Chat here', 'style': 'width: 500px; height:30px;font-size: 20px;'}), label='')
