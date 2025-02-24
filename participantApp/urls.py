from django.urls import path
from participantApp import views

urlpatterns = [
    path('participants_list/<int:event_id>/', views.ListParticipantsOnEvent.as_view(), name='participants_list'),
    path('register_participant/<int:event_id>/', views.RegistrationParticipantsView.as_view(),
         name='register_participant'),
    path('delete_participant/<int:event_id>/<int:participant_id>/', views.DeleteParticipants.as_view(),
         name='delete_participant'),
    path('favourite_participants/', views.FavouriteParticipants.as_view(), name='favourite_participants'),
    path('index', views.index, name='index'),
]