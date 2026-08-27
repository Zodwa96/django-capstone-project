"""Database models for the News Application.

This module defines the core data model for the news platform:

* :class:`CustomUser` -- an extended Django user with a role
  (Reader, Journalist, or Editor) and reader subscriptions.
* :class:`Publisher` -- a news outlet that groups editors, journalists
  and articles together.
* :class:`Article` -- a single news article written by a journalist,
  optionally linked to a publisher, and subject to editor approval.
* :class:`Newsletter` -- a curated collection of articles published by
  a journalist.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils import timezone


class CustomUser(AbstractUser):
    """A custom user model that extends Django's built-in user.

    Adds a ``role`` field (Reader, Journalist, or Editor) which is
    used throughout the app and API to control permissions, plus
    subscription relationships so that readers can follow the
    publishers and journalists whose work they are interested in.
    """
    ROLE_CHOICES = [
        ('READER', 'Reader'),
        ('JOURNALIST', 'Journalist'),
        ('EDITOR', 'Editor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='READER')

    # Reader subscriptions - FIXED: unique related_names to avoid clash
    subscribed_publishers = models.ManyToManyField(
        'Publisher', blank=True, related_name='publisher_subscribers')
    subscribed_journalists = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='journalist_subscribers',
        limit_choices_to={'role': 'JOURNALIST'}
    )

    def __str__(self):
        """Return the username together with the user's role."""
        return f"{self.username} - {self.role}"


class Publisher(models.Model):
    """A news outlet that publishes articles.

    A publisher has a set of editors (who approve articles) and
    journalists (who write articles), and readers may subscribe to a
    publisher to be notified of newly approved articles.
    """
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    editors = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='editors_publishers',
        limit_choices_to={
            'role': 'EDITOR'})
    journalists = models.ManyToManyField(
        CustomUser,
        blank=True,
        related_name='journalists_publishers',
        limit_choices_to={
            'role': 'JOURNALIST'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the publisher's name."""
        return self.name


class Article(models.Model):
    """A single news article.

    An article is written by a journalist, may optionally belong to a
    publisher, and starts out unapproved. Once an editor approves it
    (see :meth:`save`), ``approved_at`` is stamped automatically and
    the article becomes visible to readers.
    """
    title = models.CharField(max_length=200, validators=[MinLengthValidator(5)])
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='authored_articles',
        limit_choices_to={
            'role': 'JOURNALIST'})
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_articles',
        limit_choices_to={
            'role': 'EDITOR'})
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """Return the article's title."""
        return self.title

    def save(self, *args, **kwargs):
        """Save the article, stamping ``approved_at`` on first approval.

        If the article has just been marked ``approved`` and does not
        yet have an ``approved_at`` timestamp, the current time is
        recorded before the normal save proceeds.
        """
        if self.approved and not self.approved_at:
            self.approved_at = timezone.now()
        super().save(*args, **kwargs)


class Newsletter(models.Model):
    """A curated newsletter grouping together one or more articles."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='newsletters',
        limit_choices_to={
            'role': 'JOURNALIST'})
    articles = models.ManyToManyField(Article, related_name='newsletters', blank=True)

    def __str__(self):
        """Return the newsletter's title."""
        return self.title
