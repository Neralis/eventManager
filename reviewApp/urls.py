from django.urls import path
import reviewApp
from reviewApp import views
from reviewApp.views import index

urlpatterns = [
    path('review_create/<str:token>', views.ReviewCreateView.as_view(), name='review_create'),
    path('review_list/', views.ReviewListView.as_view(), name='review_list'),
    path('review_list_on_event/', views.ReviewListViewOnEvent.as_view(), name='review_list_on_event'),
    path('review_delete/<int:pk>', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('review_delete_success/', index, name='review_delete_success'),
]