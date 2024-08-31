from django.urls import path
from .views import PostListCreateView, PostRetrieveUpdateDestroyView, PostVoteView, PostTallyView

urlpatterns = [
    path('posts/<int:post_id>/vote/', PostVoteView.as_view(), name='post_vote'),
    path('posts/<int:post_id>/tally/', PostTallyView.as_view(), name='post_tally'),
]