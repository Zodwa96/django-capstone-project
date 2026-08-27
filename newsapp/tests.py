"""Automated tests for the News Application.

Covers model behaviour, role-based permissions in the browser views,
and the token-authenticated REST API endpoints.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from newsapp.models import Article, Publisher

User = get_user_model()


class TestModels(TestCase):
    """Basic sanity checks for the Article and Publisher models."""
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='JOURNALIST')
        self.publisher = Publisher.objects.create(
            name='Test Publisher', description='Test Description')
        self.article = Article.objects.create(
            title='Test Article',
            content='Test Content',
            author=self.user,
            publisher=self.publisher)

    def test_article_creation(self):
        """A newly created article stores its title and starts out unapproved."""
        self.assertEqual(self.article.title, 'Test Article')
        self.assertFalse(self.article.approved)

    def test_publisher_creation(self):
        """A newly created publisher stores its name."""
        self.assertEqual(self.publisher.name, 'Test Publisher')


class TestPermissions(TestCase):
    """Role-based access checks for the browser-facing views."""
    def setUp(self):
        self.reader_group, _ = Group.objects.get_or_create(name='Readers')
        self.journalist_group, _ = Group.objects.get_or_create(name='Journalists')
        self.editor_group, _ = Group.objects.get_or_create(name='Editors')

        self.reader = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='test123',
            role='READER')
        self.reader.groups.add(self.reader_group)

        self.journalist = User.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='test123',
            role='JOURNALIST')
        self.journalist.groups.add(self.journalist_group)

        self.publisher = Publisher.objects.create(
            name='Test Publisher', description='Test Description')
        self.article = Article.objects.create(
            title='Test Article',
            content='Test Content',
            author=self.journalist,
            publisher=self.publisher,
            approved=True)

    def test_reader_can_view_article(self):
        """A logged-in reader can load the article list page."""
        self.client.login(username='reader', password='test123')
        response = self.client.get(reverse('article_list'))
        self.assertEqual(response.status_code, 200)

    def test_journalist_can_create_article(self):
        """A logged-in journalist can submit a new article and gets redirected."""
        self.client.login(username='journalist', password='test123')
        response = self.client.post(
            reverse('article_create'), {
                'title': 'New Article', 'content': 'New Content', 'publisher': self.publisher.id})
        self.assertEqual(response.status_code, 302)


class TestAPI(APITestCase):
    """Token-authenticated checks for the newsapp REST API."""
    def setUp(self):
        self.reader_group, _ = Group.objects.get_or_create(name='Readers')
        self.journalist_group, _ = Group.objects.get_or_create(name='Journalists')
        self.editor_group, _ = Group.objects.get_or_create(name='Editors')

        self.reader = User.objects.create_user(
            username='reader',
            email='reader@example.com',
            password='test123',
            role='READER')
        self.reader.groups.add(self.reader_group)

        self.journalist = User.objects.create_user(
            username='journalist',
            email='journalist@example.com',
            password='test123',
            role='JOURNALIST')
        self.journalist.groups.add(self.journalist_group)

        self.editor = User.objects.create_user(
            username='editor',
            email='editor@example.com',
            password='test123',
            role='EDITOR')
        self.editor.groups.add(self.editor_group)

        self.publisher = Publisher.objects.create(
            name='Test Publisher', description='Test Description')
        self.publisher.publisher_subscribers.add(self.reader)

        self.article = Article.objects.create(
            title='Test Article',
            content='Test Content',
            author=self.journalist,
            publisher=self.publisher,
            approved=True)

        self.reader_token = Token.objects.create(user=self.reader)
        self.journalist_token = Token.objects.create(user=self.journalist)
        self.editor_token = Token.objects.create(user=self.editor)
        self.client = APIClient()

    def test_api_article_list(self):
        """A reader can list approved articles via the API."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reader_token.key}')
        response = self.client.get('/api/articles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_api_subscribed_articles_reader(self):
        """A reader sees only articles from publishers/journalists they follow."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reader_token.key}')
        response = self.client.get('/api/articles/subscribed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_api_article_create_journalist(self):
        """A journalist can create an article via the API."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.journalist_token.key}')
        response = self.client.post('/api/articles/create/',
                                    {'title': 'New API Article',
                                     'content': 'New API Content',
                                     'publisher': self.publisher.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_api_article_create_reader_fails(self):
        """A reader is forbidden from creating an article via the API."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.reader_token.key}')
        response = self.client.post('/api/articles/create/',
                                    {'title': 'New Article',
                                     'content': 'New Content',
                                     'publisher': self.publisher.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_article_approve_editor(self):
        """An editor can approve a pending article via the API."""
        article = Article.objects.create(
            title='Unapproved Article',
            content='Test Content',
            author=self.journalist,
            publisher=self.publisher)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.editor_token.key}')
        response = self.client.post(f'/api/articles/{article.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        article.refresh_from_db()
        self.assertTrue(article.approved)
