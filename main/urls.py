"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from voting.views import logout_view, FAQView, HomeView, RegisterView, compute_option, get_nominees, verify_id

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', RegisterView.as_view(), name='register'),
    path('admin/', admin.site.urls),
    path('logout/', logout_view, name="logout"),
    path('verify_id/', verify_id, name="verify_id"),
    path('compute_option/', compute_option, name="compute_option"),
    path('get_nominees/', get_nominees, name="get_nominees"),
    path('faqs/', FAQView.as_view(), name='faqs'),
]
