from django.urls import path
from src.apps.participantApp import views

urlpatterns = [
    path('<int:event_id>/participants_list/', views.ListParticipantsOnEvent.as_view(), name='participants_list'),
    path('<int:event_id>/register_participant/', views.RegistrationParticipantsView.as_view(),
         name='register_participant'),
    path('<int:event_id>/delete_participant/<int:participant_id>/', views.DeleteParticipants.as_view(),
         name='delete_participant'),
    path('favourite_participants/', views.FavouriteParticipants.as_view(), name='favourite_participants'),
    path('<int:event_id>/delete_participant/<int:participant_id>/reason_delete_participant/',
         views.ReasonDeleteParticipants.as_view(), name='reason_delete_participant'),
]