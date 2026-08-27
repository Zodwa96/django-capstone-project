"""Forms for the News Application.

Provides the model forms used to create and edit :class:`Article`
and :class:`Newsletter` instances from the browser-facing views.
"""
from django import forms
from .models import Article, Newsletter


class ArticleForm(forms.ModelForm):
    """Form for journalists to create or update an :class:`Article`."""
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'publisher': forms.Select(attrs={'class': 'form-control'}),
        }


class NewsletterForm(forms.ModelForm):
    """Form for journalists to create or update a :class:`Newsletter`."""
    class Meta:
        model = Newsletter
        fields = ['title', 'description', 'articles']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'articles': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
