"""Management command that creates the Reader/Journalist/Editor groups
and assigns each group the appropriate model permissions.

Run with::

    python manage.py setup_permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from newsapp.models import Article, Newsletter


class Command(BaseCommand):
    """Create the Readers, Journalists, and Editors groups with their permissions."""
    help = 'Setup groups and permissions for the news application'

    def handle(self, *args, **kwargs):
        """Create (or fetch) the three role groups and assign their permissions."""
        reader_group, _ = Group.objects.get_or_create(name='Readers')
        journalist_group, _ = Group.objects.get_or_create(name='Journalists')
        editor_group, _ = Group.objects.get_or_create(name='Editors')

        article_ct = ContentType.objects.get_for_model(Article)
        newsletter_ct = ContentType.objects.get_for_model(Newsletter)

        def get_perm(codename, ct):
            """Fetch or create a named permission for the given content type."""
            display_name = f'Can {codename.replace("_", " ")}'
            perm, _ = Permission.objects.get_or_create(
                codename=codename,
                content_type=ct,
                defaults={'name': display_name},
            )
            return perm

        reader_permissions = [
            get_perm('view_article', article_ct),
            get_perm('view_newsletter', newsletter_ct),
        ]
        reader_group.permissions.set(reader_permissions)

        journalist_permissions = [
            get_perm('view_article', article_ct),
            get_perm('add_article', article_ct),
            get_perm('change_article', article_ct),
            get_perm('delete_article', article_ct),
            get_perm('view_newsletter', newsletter_ct),
            get_perm('add_newsletter', newsletter_ct),
            get_perm('change_newsletter', newsletter_ct),
            get_perm('delete_newsletter', newsletter_ct),
        ]
        journalist_group.permissions.set(journalist_permissions)

        editor_permissions = [
            get_perm('view_article', article_ct),
            get_perm('change_article', article_ct),
            get_perm('delete_article', article_ct),
            get_perm('view_newsletter', newsletter_ct),
            get_perm('change_newsletter', newsletter_ct),
            get_perm('delete_newsletter', newsletter_ct),
        ]
        editor_group.permissions.set(editor_permissions)

        self.stdout.write(self.style.SUCCESS('Successfully setup permissions and groups'))
