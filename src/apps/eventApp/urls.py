from django.urls import path
from src.apps.eventApp import views

urlpatterns = [
    path('<int:event_id>/delete/', views.DeleteEventView.as_view(), name='event_delete'),
    path('<int:event_id>/reason_delete/', views.ReasonForDeleteEventView.as_view(), name='reason_for_delete_event'),

    path('', views.EventListView.as_view(), name='event_list'),
    path('<int:event_id>/', views.EventDetailView.as_view(), name='event_detail'),

    path('<int:event_id>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),
    path('search/', views.SearchResultView.as_view(), name='event_search'),
]