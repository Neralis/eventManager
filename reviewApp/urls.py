from django.urls import path
from reviewApp import views
from reviewApp.views import index

urlpatterns = [
    path('review_create/<str:token>/', views.ReviewCreateView.as_view(), name='review_create'),
    path('<int:user_id>/review_list/', views.ReviewListView.as_view(), name='review_list'),
    path('review_list_on_event/<int:event_id>/', views.ReviewListViewOnEvent.as_view(), name='review_list_on_event'),
    path('review_delete/<int:pk>/', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('success/', index, name='success'),
]