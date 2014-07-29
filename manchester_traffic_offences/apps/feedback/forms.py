from django import forms


class FeedbackForm(forms.Form):
    email = forms.EmailField(required=False, label="Your email address")
    question = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 50}), label="Your question")