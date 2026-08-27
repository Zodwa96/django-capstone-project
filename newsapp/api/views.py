"""REST API views for browsing, creating, and moderating articles."""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone

from newsapp.models import Article
from .serializers import ArticleSerializer
from .permissions import IsJournalist, IsEditor, IsReader


class ArticleListView(generics.ListAPIView):
    """List all approved articles."""
    queryset = Article.objects.filter(approved=True)
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class SubscribedArticlesView(generics.ListAPIView):
    """List approved articles from publishers/journalists the reader follows."""
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsReader]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        """Return approved articles matching the requesting reader's subscriptions."""
        user = self.request.user
        subscribed_publishers = user.subscribed_publishers.all()
        subscribed_journalists = user.subscribed_journalists.all()
        return Article.objects.filter(
            approved=True
        ).filter(
            models.Q(publisher__in=subscribed_publishers) |
            models.Q(author__in=subscribed_journalists)
        ).distinct()


class ArticleDetailView(generics.RetrieveAPIView):
    """Retrieve a single approved article by primary key."""
    queryset = Article.objects.filter(approved=True)
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


class ArticleCreateView(generics.CreateAPIView):
    """Let an authenticated journalist create a new article via the API."""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsJournalist]
    authentication_classes = [TokenAuthentication]

    def perform_create(self, serializer):
        """Save the new article with the requesting user as its author."""
        serializer.save(author=self.request.user)


class ArticleUpdateView(generics.UpdateAPIView):
    """Let a journalist or editor update an existing article via the API."""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsJournalist | IsEditor]
    authentication_classes = [TokenAuthentication]


class ArticleDeleteView(generics.DestroyAPIView):
    """Let a journalist or editor delete an article via the API."""
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsJournalist | IsEditor]
    authentication_classes = [TokenAuthentication]


class ArticleApprovalView(APIView):
    """Let an editor approve a pending article via the API."""
    permission_classes = [IsAuthenticated, IsEditor]
    authentication_classes = [TokenAuthentication]

    def post(self, request, article_id):
        """Mark the given article as approved by the requesting editor."""
        article = get_object_or_404(Article, id=article_id)
        article.approved = True
        article.approved_by = request.user
        article.approved_at = timezone.now()
        article.save()
        return Response({'status': 'Article approved', 'id': article.id},
                        status=status.HTTP_200_OK)
