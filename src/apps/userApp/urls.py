from django.urls import path
from src.apps.userApp import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('restore_account/', views.RestoreUserAccountRequestView.as_view(), name='restore_account_request'),
    path('recover_account/<str:token>/', views.ActivateUserView.as_view(), name='recover_account'),
    path('delete/', views.DeactivateUserView.as_view(), name='delete'),
    path("profile/", views.ProfileView.as_view(), name='profile'),
    path("profile/edit/", views.ProfileEditView.as_view(), name='profile_edit'),
    path("profile/password/", views.PasswordChangeCustomView.as_view(), name='password_change'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]