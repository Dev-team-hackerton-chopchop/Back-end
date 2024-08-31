from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Vote
from .permissions import CustomReadOnly
from .serializers import PostSerializer, PostCreateSerializer, VoteSerializer
from .xrpl_utils import create_wallet, cast_vote, tally_votes

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [CustomReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PostSerializer
        return PostCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostVoteView(APIView):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        vote_choice = request.data.get('vote_choice')
        
        if vote_choice not in ['agree', 'disagree']:
            return Response({"error": "유효하지 않은 투표 선택입니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        choice_mapping = {'agree': 'O', 'disagree': 'X'}
        db_choice = choice_mapping[vote_choice]

        wallet = create_wallet()
        try:
            result = cast_vote(wallet, str(post.vote_id), vote_choice)
            vote = Vote.objects.create(
                post=post,
                voter=request.user,
                choice=db_choice,
                transaction_hash=result['hash']
            )
            return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostTallyView(APIView):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        wallet = create_wallet()
        try:
            results = tally_votes(wallet, str(post.vote_id))
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)