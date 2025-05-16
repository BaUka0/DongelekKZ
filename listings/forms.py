from django import forms
from .models import Car, Brand, Model

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'mileage', 'price', 'description', 'image']
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-control'}),  # Бренд үшін ашылмалы тізім
            'model': forms.Select(attrs={'class': 'form-control'}),  # Модель үшін ашылмалы тізім
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2025, 'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Бренд атауы'})
        }

class ModelForm(forms.ModelForm):
    class Meta:
        model = Model
        fields = ['name', 'brand']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Модель атауы'}),
            'brand': forms.Select(attrs={'class': 'form-control'})
        }