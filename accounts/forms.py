from django import forms
from core.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from datetime import date
import re

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    location = forms.CharField(label='Город/Страна')

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'birth_date', 'location', 'phone', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [c for c in User.ROLE_CHOICES if c[0] in ('client', 'master')]
        self.fields['phone'].help_text = 'Формат: +37529XXXXXXX'

    def clean_birth_date(self):
        value = self.cleaned_data['birth_date']
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValidationError('Пользователь должен быть старше 18 лет.')
        return value

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not re.match(r'^\+37529\d{7}$', phone):
            raise ValidationError('Телефон должен быть в формате +37529XXXXXXX')
        if User.objects.filter(phone=phone).exists():
            raise ValidationError('Пользователь с таким телефоном уже существует.')
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', 'Пароли не совпадают')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput) 