from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Message, Report


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone", "role", "password1", "password2")


class UserEditForm(UserChangeForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "role", "avatar", "is_active")


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("recipient", "subject", "content", "attachment")


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("report_type", "title", "content", "attachment", "status")
