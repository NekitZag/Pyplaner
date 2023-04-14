# """Определяет схемы url для пользователей"""

from django.urls import path, include

from django.contrib.auth import views
from django.urls import path
from .views import render_logout
app_name= 'users'
urlpatterns = [
    #включить url авторизации по умолчанию
    path('login/', views.LoginView.as_view(), name='login'),
    path('redirect/', render_logout, name='logout'),


]