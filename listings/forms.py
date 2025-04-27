from django import forms
from .models import Car

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'mileage', 'price', 'description', 'image']
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-control'}),  # Выпадающий список для бренда
            'model': forms.Select(attrs={'class': 'form-control'}),  # Выпадающий список для модели
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2025, 'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }