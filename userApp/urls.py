from django.urls import path
from userApp import views

urlpatterns = [
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('restore_account/', views.RestoreUserAccountRequestView.as_view(), name='restore_account_request'),
    path('recover_account/<str:token>/', views.ActivateUserView.as_view(), name='recover_account'),
    path('<int:user_id>/delete/', views.DeactivateUserView.as_view(), name='delete'),
]