"""Views for the blog app."""
from django.shortcuts import render
from django.utils import timezone
from .models import Post


def post_list(request):
    """Render post list on the webpage."""
    posts = (
        Post.objects.
        filter(published_date__lte=timezone.now()).
        order_by('published_date')
    )
    return render(request, 'blog/post_list.html', {'posts': posts})
