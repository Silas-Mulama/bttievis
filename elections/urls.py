from django.urls import path
from . import views



urlpatterns = [
    # Elections list
    path('vote/elections/', views.elections, name='elections'),
    path('vote/elections/', views.elections_done, name='elections_done'),

    # Summary page: positions + candidates + voting
    path('vote/election/<uuid:election_id>/summary/', views.election_summary, name='election_summary'),

    # Voting
    path('vote/candidate/<int:candidate_id>/', views.vote_candidate, name='vote_candidate'),
    path('vote/<uuid:election_id>/position/abstain/', views.abstain_vote, name='abstain'),


    # Results

path('vote/<uuid:election_id>/result/', views.vote_result, name='vote_result'),

]

