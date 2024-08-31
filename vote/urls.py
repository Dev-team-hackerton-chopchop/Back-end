# vote/urls.py

from django.urls import path
from .views import VoteTransaction, TallyVotes

urlpatterns = [
    path('vote/', VoteTransaction.as_view(), name='vote_transaction'),
    path('tally/', TallyVotes.as_view(), name='tally_votes'),

]
