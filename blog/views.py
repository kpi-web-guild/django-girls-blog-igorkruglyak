"""Views for the blog app."""
from django.shortcuts import render


def post_list(request):
    """Render post list on the webpage."""
    return render(request, 'blog/post_list.html', {})
