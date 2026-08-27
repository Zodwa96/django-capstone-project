"""DRF serializers for the newsapp REST API."""
from rest_framework import serializers
from newsapp.models import Article, Newsletter


class ArticleSerializer(serializers.ModelSerializer):
    """Serializes :class:`~newsapp.models.Article` instances for the API.

    Adds read-only ``author_name`` and ``publisher_name`` convenience
    fields alongside the raw foreign key ids, and marks the
    system-managed fields (id, timestamps, author, approval status)
    as read-only so clients cannot set them directly.
    """
    author_name = serializers.CharField(source='author.username', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True, default=None)

    class Meta:
        model = Article
        fields = [
            'id',
            'title',
            'content',
            'author',
            'author_name',
            'publisher',
            'publisher_name',
            'created_at',
            'approved',
            'approved_at']
        read_only_fields = ['id', 'created_at', 'approved_at', 'author', 'approved']


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializes :class:`~newsapp.models.Newsletter` instances for the API."""
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Newsletter
        fields = ['id', 'title', 'description', 'author', 'author_name', 'created_at', 'articles']
        read_only_fields = ['id', 'created_at', 'author']
