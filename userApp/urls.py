from django.urls import path
from eventApp import views
from .views import register, user_login, Profile, ProfileEdit
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("events/", views.EventListView.as_view(), name="event_list"),
    path("profile/<int:pk>/", Profile.as_view(), name="profile"),
    path("profile/<int:pk>/edit", ProfileEdit.as_view(), name="profile_edit"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)