from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)
    city = forms.CharField(required=False, max_length=80)
    phone = forms.CharField(required=False, max_length=30)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.city = self.cleaned_data.get("city", "")
            profile.phone = self.cleaned_data.get("phone", "")
            profile.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["city", "phone"]
