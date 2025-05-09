from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.core.mail import send_mail
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import CustomUser, OTPCode
from .forms import CustomUserCreationForm, ProfileUpdateForm, OTPVerificationForm
import random

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login_with_otp')                                                                                                                                                                                                                                                                                                                                                                                                                                    
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        send_otp(user)
        self.request.session['user_id'] = user.id
        return redirect('login_with_otp')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        return self.request.user

def send_otp(user):
    code = f"{random.randint(100000, 999999)}"
    OTPCode.objects.update_or_create(user=user, defaults={'code': code})
    send_mail(
        'Ваш одноразовый код',
        f'Ваш код для входа: {code}',
        'bauirzhan.bisan@yandex.ru',
        [user.email],
        fail_silently=False,
    )

def login_with_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Сессия истекла. Пожалуйста, зарегистрируйтесь или войдите снова.')
        return redirect('signup')

    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                otp = OTPCode.objects.get(user=user, code=code)
                if otp.is_valid():
                    user.is_active = True
                    user.save()
                    login(request, user)
                    otp.delete()
                    del request.session['user_id']
                    return redirect('index')
                else:
                    messages.error(request, 'Код истек. Попробуйте снова.')
                    return render(request, 'accounts/otp_verification.html', {'form': form})
            except OTPCode.DoesNotExist:
                messages.error(request, 'Неверный код.')
                return render(request, 'accounts/otp_verification.html', {'form': form})
    else:
        send_otp(user)  # Отправляем код повторно
        form = OTPVerificationForm()
        messages.info(request, 'Код отправлен на вашу почту.')

    return render(request, 'accounts/otp_verification.html', {'form': form})

def resend_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Сессия истекла. Пожалуйста, зарегистрируйтесь или войдите снова.')
        return redirect('signup')

    user = CustomUser.objects.get(id=user_id)
    send_otp(user)
    messages.success(request, 'Код был переотправлен на вашу почту.')
    return HttpResponseRedirect(reverse('login_with_otp'))