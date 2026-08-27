"""URL routes for the newsapp REST API, including token auth and article endpoints."""
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('token/', obtain_auth_token, name='api_token_auth'),
    path('articles/', views.ArticleListView.as_view(), name='api_article_list'),
    path('articles/subscribed/', views.SubscribedArticlesView.as_view(),
         name='api_subscribed_articles'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(),
         name='api_article_detail'),
    path('articles/create/', views.ArticleCreateView.as_view(),
         name='api_article_create'),
    path('articles/<int:pk>/update/', views.ArticleUpdateView.as_view(),
         name='api_article_update'),
    path('articles/<int:pk>/delete/', views.ArticleDeleteView.as_view(),
         name='api_article_delete'),
    path('articles/<int:article_id>/approve/', views.ArticleApprovalView.as_view(),
         name='api_article_approve'),
]
