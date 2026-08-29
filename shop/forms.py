from django import forms

from .models import Review


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)])
    text = forms.CharField(widget=forms.Textarea, max_length=1000)
