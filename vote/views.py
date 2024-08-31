from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .xrpl_utils import cast_vote, create_wallet, tally_votes

class VoteTransaction(APIView):
    def post(self, request):
        post_id = request.data.get('post_id')
        vote_choice = request.data.get('vote_choice')  # "O" 또는 "X"
        
        wallet = create_wallet()

        try:
            # 트랜잭션에 투표 기록을 저장
            cast_vote(wallet, post_id, "", vote_choice)
            return Response({"status": "Transaction submitted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TallyVotes(APIView):
    def post(self, request):
        post_id = request.data.get('post_id')
        
        wallet = create_wallet()

        try:
            results = tally_votes(wallet, post_id)
            return Response({"results": results}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
