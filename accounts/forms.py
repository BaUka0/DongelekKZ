from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, SellerApplication

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'avatar', 'bio')

class CustomUserChangeForm(UserChangeForm):
    password = None
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'avatar', 'bio', 'is_active', 'is_staff', 'groups', 'user_permissions')

class ProfileUpdateForm(forms.ModelForm):
     class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'avatar', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

class OTPVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, label="Введите код", widget=forms.TextInput(attrs={'class': 'form-control'}))

class SellerApplicationForm(forms.ModelForm):
    class Meta:
        model = SellerApplication
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Сатушы болу себебіңізді жазыңыз...'
            }),
        }
        labels = {
            'reason': 'Сатушы болу себебі',
        }
        help_texts = {
            'reason': 'Өзіңіз жайлы және неліктен сатушы болғыңыз келетінін жазыңыз',
        }