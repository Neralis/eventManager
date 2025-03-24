from django.urls import path
from userApp import views

urlpatterns = [
    path('<int:pk>/delete/', views.DeactivateUserView.as_view(), name='delete'),
    path('success/', views.index, name='success'),
]