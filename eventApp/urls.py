from django.urls import path
from eventApp import views

urlpatterns = [
    path('<int:event_id>/delete/', views.DeleteEventView.as_view(), name='delete_event'),
    path('<int:event_id>/reason_delete/', views.ReasonForDeleteEventView.as_view(), name='reason_for_delete_event'),
]