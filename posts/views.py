from django.shortcuts import render
from users.models import Profile
from .models import Post
from .permissions import CustomReadOnly
from .serializers import PostSerializer, PostCreateSerializer

from rest_framework import status
from vote.views import VoteTransaction, TallyVotes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404


# Create your views here.
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [CustomReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'likes']

    def get_serializer_class(self):
        if self.action == 'list' or 'retrieve':
            return PostSerializer
        return PostCreateSerializer

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(author=self.request.user, profile=profile)

class PostVoteView(APIView):
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if not post.vote_enabled:
            return Response({"error": "투표가 활성화되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        vote_choice = request.data.get('vote_choice')
        
        vote_transaction = VoteTransaction()
        vote_response = vote_transaction.post(request._request)
        
        if vote_response.status_code == status.HTTP_200_OK:
            return Response({"message": "투표가 성공적으로 제출되었습니다."}, status=status.HTTP_200_OK)
        else:
            return vote_response

class PostTallyView(APIView):
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if not post.vote_enabled:
            return Response({"error": "투표가 활성화되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        tally_votes = TallyVotes()
        tally_response = tally_votes.post(request._request)
        
        return tally_response