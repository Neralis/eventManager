from django.urls import path
from src.apps.reviewApp import views

urlpatterns = [
    path('review_create/<str:token>/', views.ReviewCreateView.as_view(), name='review_create'),
    path('review_list/', views.ReviewListView.as_view(), name='review_list'),
    path('<int:event_id>/review_list_on_event/', views.ReviewListViewOnEvent.as_view(), name='review_list_on_event'),
    path('review_delete/<int:review_id>/', views.ReviewDeleteView.as_view(), name='review_delete'),
]