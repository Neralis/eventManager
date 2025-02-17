from django.urls import path
from . import views


urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),

    path('<int:pk>/update/', views.EventUpdateView.as_view(), name='event_update'),
    path('create/', views.EventCreateView.as_view(), name='event_create'),

]