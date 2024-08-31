from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, PostVoteView, PostTallyView

router = DefaultRouter()
router.register(r'', PostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/vote/', PostVoteView.as_view(), name='post-vote'),
    path('<int:pk>/tally/', PostTallyView.as_view(), name='post-tally'),
]