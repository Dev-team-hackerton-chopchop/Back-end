from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Post, Vote

# from .permissions import CustomReadOnly

from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer, PostCreateSerializer, VoteSerializer
from .xrpl_utils import get_wallet, cast_vote, tally_votes

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return PostSerializer
        return PostCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostVoteView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="게시글에 대한 투표를 생성합니다.",
        manual_parameters=[
            openapi.Parameter(
                'pk', 
                openapi.IN_PATH, 
                description="투표할 게시글의 ID", 
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['choice'],
            properties={
                'choice': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description="'O' (동의) 또는 'X' (비동의)"
                )
            }
        ),
        responses={
            status.HTTP_201_CREATED: VoteSerializer,
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description="잘못된 요청",
                examples={
                    "application/json": {
                        "error": "오류 메시지"
                    }
                }
            ),
            status.HTTP_404_NOT_FOUND: "게시글을 찾을 수 없음"
        }
    )
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        choice = request.data.get('choice')
        
        if not choice:
            return Response({"error": "투표 선택이 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        if choice not in ['O', 'X']:
            return Response({"error": "유효하지 않은 투표 선택입니다. 'O' 또는 'X'를 선택해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 이미 투표한 경우 체크
        if Vote.objects.filter(post=post, voter=request.user).exists():
            return Response({"error": "이미 이 게시글에 투표하셨습니다."}, status=status.HTTP_400_BAD_REQUEST)

        wallet = get_wallet()
        try:
            result = cast_vote(wallet, str(post.vote_id), "", choice)
            vote = Vote.objects.create(
                post=post,
                voter=request.user,
                choice=choice,
                transaction_hash=result['hash']
            )
            return Response(VoteSerializer(vote).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"투표 처리 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class PostTallyView(APIView):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        wallet = get_wallet()
        try:
            results = tally_votes(wallet, str(post.vote_id))
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)