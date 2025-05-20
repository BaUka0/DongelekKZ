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
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import CustomUser, OTPCode, SellerApplication
from .forms import CustomUserCreationForm, ProfileUpdateForm, OTPVerificationForm, SellerApplicationForm
import random
import os
from django.conf import settings

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login_with_otp')                                                                                                                                                                                                                                                                                                                                                                                                                                    
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        send_otp(user)
        self.request.session['user_id'] = user.id
        self.request.session['otp_sent'] = True  # Set flag to indicate OTP was sent
        return redirect('login_with_otp')

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('index')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.instance
        remove_avatar = self.request.POST.get('remove_avatar') == 'true'
        
        if remove_avatar and user.avatar and user.avatar.name != user.DEFAULT_AVATAR_PATH:
            # Set to default avatar instead of None
            user.set_default_avatar()
            messages.success(self.request, 'Аватар өзгерді. Стандартты аватар орнатылды.')
            return redirect(self.success_url)
        
        response = super().form_valid(form)
        return response

def send_otp(user):
    code = f"{random.randint(100000, 999999)}"
    OTPCode.objects.update_or_create(user=user, defaults={'code': code})
    send_mail(
        'Сіздің бір реттік кодыңыз',
        f'Кіру үшін кодыңыз: {code}',
        'bauirzhan.bisan@yandex.ru',
        [user.email],
        fail_silently=False,
    )

def login_with_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Сессия аяқталды. Тіркеліңіз немесе қайта кіріңіз.')
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
                    if 'otp_sent' in request.session:
                        del request.session['otp_sent']
                    return redirect('index')
                else:
                    messages.error(request, 'Код мерзімі өтіп кетті. Қайталап көріңіз.')
                    return render(request, 'accounts/otp_verification.html', {'form': form})
            except OTPCode.DoesNotExist:
                messages.error(request, 'Қате код.')
                return render(request, 'accounts/otp_verification.html', {'form': form})
    else:
        # Only send a new OTP if one wasn't sent already during signup
        if not request.session.get('otp_sent'):
            send_otp(user)
            messages.info(request, 'Код сіздің поштаңызға жіберілді.')
        else:
            # If already sent, just display the message without sending a new code
            messages.info(request, 'Поштаңызға жіберілген кодты енгізіңіз.')
            # Reset the flag for future requests if needed
            request.session['otp_sent'] = False
            
        form = OTPVerificationForm()

    return render(request, 'accounts/otp_verification.html', {'form': form})

def resend_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'Сессия аяқталды. Тіркеліңіз немесе қайта кіріңіз.')
        return redirect('signup')

    user = CustomUser.objects.get(id=user_id)
    send_otp(user)
    # Set the flag to avoid automatic resending in the login_with_otp view
    request.session['otp_sent'] = True
    messages.success(request, 'Код сіздің поштаңызға қайта жіберілді.')
    return HttpResponseRedirect(reverse('login_with_otp'))

@login_required
def become_seller(request):
    """
    View to handle user requests to apply to become a seller
    """
    # Check if user is already a seller
    if request.user.is_seller:
        messages.info(request, 'Сіз қазірдің өзінде сатушысыз.')
        return redirect('index')
    
    # Check if user already has a pending application
    existing_application = SellerApplication.objects.filter(
        user=request.user, 
        status='pending'
    ).first()
    
    if existing_application:
        messages.info(request, 'Сіздің өтінішіңіз қаралуда. Күте тұрыңыз.')
        return render(request, 'accounts/application_status.html', {
            'application': existing_application
        })
    
    # Check if user has a rejected application
    rejected_application = SellerApplication.objects.filter(
        user=request.user, 
        status='rejected'
    ).order_by('-created_at').first()
    
    if request.method == 'POST':
        form = SellerApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            
            messages.success(request, 'Сіздің өтінішіңіз қабылданды. Әкімші қарағаннан кейін хабарланамыз.')
            return redirect('application_status')
    else:
        # Pre-fill the form with reason from a rejected application if it exists
        initial_data = {}
        if rejected_application:
            initial_data = {'reason': rejected_application.reason}
        
        form = SellerApplicationForm(initial=initial_data)
    
    context = {
        'form': form,
        'rejected_application': rejected_application
    }
    return render(request, 'accounts/become_seller.html', context)

@login_required
def application_status(request):
    """
    View to show the status of a user's seller application
    """
    applications = SellerApplication.objects.filter(user=request.user).order_by('-created_at')
    
    if not applications.exists():
        messages.info(request, 'Сізде әлі өтініш жоқ.')
        return redirect('become_seller')
    
    return render(request, 'accounts/application_status.html', {
        'applications': applications,
        'current_application': applications.first()
    })