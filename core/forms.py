from django import forms
from .models import Review, Appointment, MasterProfile, Service

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        exclude = ['user', 'name', 'date']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }

class AppointmentForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), widget=forms.CheckboxSelectMultiple)
    master = forms.ModelChoiceField(queryset=MasterProfile.objects.all())
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    class Meta:
        model = Appointment
        fields = ['services', 'master', 'car_type', 'date', 'time'] 