"""Django admin site configuration for the News Application models."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Publisher, Article, Newsletter


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for :class:`CustomUser`.

    Extends Django's built-in ``UserAdmin`` with the extra ``role``
    and subscription fields defined on the custom user model.
    """
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'subscribed_publishers', 'subscribed_journalists')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Admin configuration for :class:`Publisher`."""
    list_display = ('name', 'created_at')
    filter_horizontal = ('editors', 'journalists')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin configuration for :class:`Article`, with search and filters."""
    list_display = ('title', 'author', 'publisher', 'approved', 'created_at', 'approved_at')
    list_filter = ('approved', 'publisher')
    search_fields = ('title', 'content')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin configuration for :class:`Newsletter`."""
    list_display = ('title', 'author', 'created_at')
    filter_horizontal = ('articles',)
