"""URL routes for the browser-facing newsapp views (articles and newsletters)."""
from django.urls import path
from . import views

urlpatterns = [
    path('articles/', views.article_list, name='article_list'),
    path('articles/<int:article_id>/', views.article_detail, name='article_detail'),
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<int:article_id>/approve/', views.article_approve, name='article_approve'),
    path('articles/<int:article_id>/update/', views.article_update, name='article_update'),
    path('articles/<int:article_id>/delete/', views.article_delete, name='article_delete'),
    path('newsletters/', views.newsletter_list, name='newsletter_list'),
    path('newsletters/create/', views.newsletter_create, name='newsletter_create'),
    path('pending-articles/', views.pending_articles, name='pending_articles'),
]
