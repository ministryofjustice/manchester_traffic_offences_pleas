from django import forms

class FeedbackForm(forms.Form):
    feedback_email = forms.EmailField(label="Your email address",
    	                              required=False,
    	                              help_text="We'll only use this to reply to your message.",
    	                              widget=forms.TextInput(attrs={"class": "form-control-wide"}))

    feedback_question = forms.CharField(label="Your feedback",
    	                                required=True,
    	                                error_messages={"required": "Please provide us with some feedback"},
    	                                widget=forms.Textarea(attrs={"rows": 5, 
    	                                                             "cols": 50, 
    	                                                             "class": "form-control-wide"}))