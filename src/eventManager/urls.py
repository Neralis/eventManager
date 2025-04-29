"""
URL configuration for eventManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from django.conf.urls.static import static
from django.views.generic import RedirectView
from src.eventManager import settings
from src.utils import error_handler

handler403 = error_handler.handler403
handler404 = error_handler.handler404
handler500 = error_handler.handler500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('events/', include('src.apps.eventApp.urls')),
    path('reviews/', include('src.apps.reviewApp.urls')),
    path('participants/', include('src.apps.participantApp.urls')),
    path('users/', include('src.apps.userApp.urls')),
    path('', RedirectView.as_view(url='events/')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)