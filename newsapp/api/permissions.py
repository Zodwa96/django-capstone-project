"""Custom DRF permission classes based on the CustomUser ``role`` field.

Each permission checks the user's ``role`` field first, falling back
to Django group membership, so that the API respects the same
role/group system used by the browser-facing views.
"""
from rest_framework import permissions


class IsJournalist(permissions.BasePermission):
    """Allow access only to authenticated journalists."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'JOURNALIST' or request.user.groups.filter(
                name='Journalists').exists()
        )


class IsEditor(permissions.BasePermission):
    """Allow access only to authenticated editors."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'EDITOR' or request.user.groups.filter(name='Editors').exists()
        )


class IsReader(permissions.BasePermission):
    """Allow access only to authenticated readers."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'READER' or request.user.groups.filter(name='Readers').exists()
        )
