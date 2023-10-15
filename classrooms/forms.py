from django import forms
from .models import Teacher, Student


class GenerateCertificateForm(forms.Form):
    teacher = forms.ModelChoiceField(
        queryset=Teacher.objects.all(), empty_label="Select a teacher"
    )
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(), empty_label="Select a student"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        field_attributes = {"class": "w-full px-3 py-3 border border-gray-300 rounded"}
        for field in self.fields:
            self.fields[field].widget.attrs.update(field_attributes)


class VerifyCertificateForm(forms.Form):
    certificate_token = forms.CharField(max_length=500)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        field_attributes = {
            "class": "w-full px-3 py-3 border border-gray-300 rounded",
            "placeholder": "Enter certificate token",
        }
        for field in self.fields:
            self.fields[field].widget.attrs.update(field_attributes)
