from django import forms


class FeedbackForm(forms.Form):
    feedback_email = forms.EmailField(required=False, label="Your email address")
    feedback_question = forms.CharField(widget=forms.Textarea(attrs={"rows": 5, "cols": 50}), label="Your question")