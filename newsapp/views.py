"""Views for the News Application.

Handles the browser-facing (non-API) workflows: browsing and managing
articles, creating newsletters, and account registration. Also
contains the two helper functions that are triggered when an article
is approved: emailing subscribers and posting the approved article to
the internal API.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils import timezone
from django.contrib.auth import get_user_model
import requests
import logging

from .models import Article, Newsletter
from .forms import ArticleForm, NewsletterForm

User = get_user_model()
logger = logging.getLogger(__name__)


def is_editor(user):
    """Return True if the given user has editor privileges."""
    return user.is_authenticated and (
        user.role == 'EDITOR' or user.groups.filter(name='Editors').exists())


def is_journalist(user):
    """Return True if the given user has journalist privileges."""
    return user.is_authenticated and (
        user.role == 'JOURNALIST' or user.groups.filter(name='Journalists').exists())


def home(request):
    """Show the public landing page with the ten most recent approved articles."""
    articles = Article.objects.filter(approved=True).order_by('-created_at')[:10]
    return render(request, 'newsapp/home.html', {'articles': articles})


@login_required
def article_list(request):
    """List all approved articles for logged-in users."""
    articles = Article.objects.filter(approved=True)
    return render(request, 'newsapp/article_list.html', {'articles': articles})


@login_required
def article_detail(request, article_id):
    """Show the full detail view of a single approved article."""
    article = get_object_or_404(Article, id=article_id, approved=True)
    return render(request, 'newsapp/article_detail.html', {'article': article})


@login_required
@user_passes_test(is_journalist)
def article_create(request):
    """Let a journalist submit a new article, pending editor approval."""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Article created successfully! Awaiting approval.')
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'newsapp/article_form.html', {'form': form})


@login_required
@user_passes_test(is_journalist)
def article_update(request, article_id):
    """Let a journalist edit one of their own articles."""
    article = get_object_or_404(Article, id=article_id, author=request.user)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated.')
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)
    return render(request, 'newsapp/article_form.html', {'form': form})


@login_required
@user_passes_test(is_journalist)
def article_delete(request, article_id):
    """Delete an article.

    The author may delete their own article; an editor may delete any
    article. Anyone else is redirected with a permission error.
    """
    article = get_object_or_404(Article, id=article_id)
    # Journalist can delete own, editor can delete any
    if article.author != request.user and not is_editor(request.user):
        messages.error(request, 'Permission denied.')
        return redirect('article_list')
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted.')
        return redirect('article_list')
    return render(request, 'newsapp/article_confirm_delete.html', {'article': article})


@login_required
def pending_articles(request):
    """Show editors the list of articles awaiting approval."""
    if not is_editor(request.user):
        messages.error(request, 'Editors only.')
        return redirect('home')
    articles = Article.objects.filter(approved=False).order_by('-created_at')
    return render(request, 'newsapp/pending_articles.html', {'articles': articles})


@login_required
@user_passes_test(is_editor)
def article_approve(request, article_id):
    """Let an editor approve a pending article, triggering notifications."""
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.approved = True
        article.approved_by = request.user
        article.approved_at = timezone.now()
        article.save()
        messages.success(request, 'Article approved successfully!')
        return redirect('pending_articles')
    return render(request, 'newsapp/article_approve.html', {'article': article})

# --- Helpers (fixed: standalone functions, not methods) ---


def send_approval_notifications(article):
    """Email everyone subscribed to the article's publisher or author.

    Builds the set of subscribers from both the publisher's
    subscriber list and the author's personal follower list, then
    sends each of them a plain-text notification email. Failures for
    an individual recipient are logged rather than raised, so one bad
    address does not block the rest.
    """
    subscribers = set()
    if article.publisher:
        subscribers.update(article.publisher.publisher_subscribers.all())
    # journalist subscribers: users who subscribed to this author
    subscribers.update(article.author.journalist_subscribers.all())

    for user in subscribers:
        if not user.email:
            continue
        try:
            publisher_name = article.publisher.name if article.publisher else 'Independent'
            article_url = f'{settings.SITE_URL}/articles/{article.id}/'
            message = (
                f'Dear {user.username},\n\n'
                f'A new article has been approved:\n\n'
                f'Title: {article.title}\n'
                f'Author: {article.author.username}\n'
                f'Publisher: {publisher_name}\n\n'
                f'Read it at: {article_url}'
            )
            send_mail(
                f'New Article Approved: {article.title}',
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Error sending email to {user.email}: {e}")


def post_to_api(article):
    """Notify the internal API that an article has been approved.

    Sends a short-timeout POST request describing the article to the
    site's own ``/api/approved/`` endpoint. Network or non-2xx
    failures are logged as warnings and swallowed, since this is a
    best-effort side effect and should never block the approval flow.
    """
    try:
        api_url = f"{settings.SITE_URL}/api/approved/"
        data = {
            'title': article.title,
            'content': article.content,
            'author': article.author.username,
            'publisher': article.publisher.name if article.publisher else None,
            'approved_at': article.approved_at.isoformat() if article.approved_at else None,
        }
        response = requests.post(api_url, json=data, timeout=5)
        if response.status_code not in (200, 201):
            logger.warning(f"API post failed with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.warning(f"API request failed: {e}")


@login_required
def newsletter_list(request):
    """List all newsletters, most recent first."""
    newsletters = Newsletter.objects.all().order_by('-created_at')
    return render(request, 'newsapp/newsletter_list.html', {'newsletters': newsletters})


@login_required
@user_passes_test(is_journalist)
def newsletter_create(request):
    """Let a journalist compile a newsletter from existing articles."""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            nl = form.save(commit=False)
            nl.author = request.user
            nl.save()
            form.save_m2m()
            messages.success(request, 'Newsletter created!')
            return redirect('newsletter_list')
    else:
        form = NewsletterForm()
    return render(request, 'newsapp/newsletter_form.html', {'form': form})


def register(request):
    """Handle self-service account registration.

    Readers and journalists may register themselves directly; anyone
    requesting the Editor role is downgraded to Reader, since editor
    accounts must be assigned by an administrator.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'READER')

        if role not in ['READER', 'JOURNALIST', 'EDITOR']:
            role = 'READER'
        # Only allow READER/JOURNALIST self-registration for security
        if role == 'EDITOR':
            messages.error(request, 'Editor role requires admin assignment.')
            role = 'READER'

        try:
            user = User.objects.create_user(
                username=username, email=email, password=password, role=role)
            # Assign group
            group_name = 'Readers' if role == 'READER' else 'Journalists'
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            user.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    return render(request, 'registration/register.html')
