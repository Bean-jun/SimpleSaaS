from django.urls import path
from . import views


app_name = 'app01'


urlpatterns = [
    path('sms/', views.sms, name='sms'),
    path('register/', views.register, name='register'),
]
