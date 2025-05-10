from django import forms
from .models import LabBooking, LabTest

class LabBookingForm(forms.ModelForm):
    # Modify the queryset to filter tests based on their names or identifiers
    test = forms.ModelChoiceField(
        queryset=LabTest.objects.filter(name__in=[
            "Complete blood count (CBC)",
            "Alanine transaminase (ALT)",
            "Thyroid stimulating hormone (TSH)",
            "Thyroglobulin antibodies (TgAb)",
            "Blood sugar (glucose) tests",
            "Vitamin B12 test"
        ]),
        label="Select Test"
    )

    class Meta:
        model = LabBooking
        fields = ['test', 'date', 'time_slot', 'patient_name', 'phone_number', 'address']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time_slot': forms.TimeInput(attrs={'type': 'time'}),
            'patient_name': forms.TextInput(attrs={'placeholder': 'Enter patient name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter address', 'rows': 3}),
        }