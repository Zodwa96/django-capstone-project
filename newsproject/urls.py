"""Top-level URL configuration for the newsproject Django project.

Wires up the admin site, authentication views, the newsapp browser
views, and the newsapp REST API under the ``/api/`` prefix.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from newsapp import views as news_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', news_views.home, name='home'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html'),
        name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', news_views.register, name='register'),
    path('', include('newsapp.urls')),
    path('api/', include('newsapp.api.urls')),
]
