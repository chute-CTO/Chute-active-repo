from django import forms

from django.contrib.auth.models import User
from laundrytaskerapp.models import Laundromat, Service

class UserForm(forms.ModelForm):
    email = forms.CharField(max_length=100, required=True)
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name", "email")


class UserFormForEdit(forms.ModelForm):
    email = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

class LaundromatForm(forms.ModelForm):
    class Meta:
        model = Laundromat
        fields = ("name", "phone", "address", "logo")

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        exclude = ("laundromat",)
