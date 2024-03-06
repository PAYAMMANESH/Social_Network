from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile


class UserRegisterForm(forms.Form):
    username = forms.CharField(min_length=5,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'your name'}))
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your email address'}))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'your password'}))

    password2 = forms.CharField(label="confirm password",
                                widget=forms.PasswordInput(
                                    attrs={"class": 'form-control', 'placeholder': 'your passwprd'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        user = User.objects.filter(email=email).exists()
        if user:
            raise ValidationError("Email already registered")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        user = User.objects.filter(username=username).exists()
        if user:
            raise ValidationError("Username already registered")
        return username

    def clean(self):
        cd = super().clean()
        p1 = cd.get('password1')
        p2 = cd.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("password must match")


class UserLoginForm(forms.Form):
    username = forms.CharField(min_length=5,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'your name'}))

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'your password'}))


class EditUserForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ('age', 'bio')
