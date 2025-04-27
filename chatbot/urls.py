# chatbot/urls.py
from django.urls import path
from . import views

app_name = 'chatbot' # Пространство имен

urlpatterns = [
    path('get_response/', views.get_response, name='get_response'),
    path('clear_history/', views.clear_history, name='clear_history'),
    path('load_history/', views.load_history, name='load_history'),
    path('voice-input/', views.voice_input, name='voice_input'),
]