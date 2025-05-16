from django.urls import path
from .views import SignUpView, ProfileUpdateView, login_with_otp, resend_otp, become_seller

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', ProfileUpdateView.as_view(), name='profile_update'),
    path('login/otp/', login_with_otp, name='login_with_otp'),
    path('login/otp/resend/', resend_otp, name='resend_otp'),
    path('become-seller/', become_seller, name='become_seller'),
]
