from django.urls import path
from . import views


urlpatterns = [

    path('', views.EventListView.as_view(), name='event_list'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),

    path('<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('delete/<int:pk>/', views.EventDeleteAjaxView.as_view(), name='event_delete'),
    path('search/', views.SearchResultView.as_view(), name = 'event_search'),
    path('<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('<int:event_id>/registration_not_auth_user/', views.registration_not_auth_user, name='registration_form'),



]