from django import forms


class FeedbackForm(forms.Form):
    email = forms.EmailField(required=False)
    feedback = forms.CharField(widget=forms.TextInput)