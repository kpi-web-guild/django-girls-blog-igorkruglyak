"""Tests for views are at this file."""
from unittest.mock import patch
from datetime import datetime

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from blog.models import Post


class ViewsTest(TestCase):
    """Testing class for views."""

    USERNAME = 'admin'
    PASSWORD = '12345678'

    def setUp(self):
        """Prepare data for testing."""
        self.client = Client()
        self.user = User.objects.create(
            username='testuser',
            password='blablabla',
            is_superuser=True, is_staff=True,
            email='testuser@gmail.com',
            is_active=True,
        )

    def test_index_view_rendering(self):
        """Testing main page for render needed posts."""
        time_zone = timezone.get_current_timezone()
        post = Post.objects.create(
            author=self.user, title='Test',
            text='superText',
            created_date=datetime(
                day=1, month=3,
                year=2020, tzinfo=time_zone,
            ),
            published_date=datetime(
                day=1, month=3,
                year=2020,
                tzinfo=time_zone,
            ),
        )
        past_post = Post.objects.create(
            author=self.user, title='past_est',
            text='superText',
            created_date=datetime(
                day=1, month=4,
                year=2019,
                tzinfo=time_zone,
            ),
            published_date=datetime(
                day=1, month=4,
                year=2019,
                tzinfo=time_zone,
            ),
        )
        future_post = Post.objects.create(
            author=self.user,
            title='future_test',
            text='superText',
            created_date=datetime(
                day=1, month=4,
                year=2120,
                tzinfo=time_zone,
            ),
            published_date=datetime(
                day=1,
                month=4,
                year=2120,
                tzinfo=time_zone,
            ),
        )
        with patch(
                'django.utils.timezone.now', lambda: datetime(
                    day=1,
                    month=1,
                    year=2020,
                    tzinfo=time_zone,
                ),
        ):
            response = self.client.get(reverse('post_list'))
            self.assertListEqual(list(response.context['posts']), [past_post])
            self.assertNotContains(response, post)
            self.assertNotContains(response, future_post)
        with patch(
                'django.utils.timezone.now', lambda: datetime(
                    day=1,
                    month=4,
                    year=2020,
                    tzinfo=time_zone,
                ),
        ):
            response = self.client.get(reverse('post_list'))
            self.assertListEqual(
                list(response.context['posts']), [
                    post,
                    past_post,
                ],
            )
            self.assertNotContains(response, future_post)
        with patch(
                'django.utils.timezone.now', lambda: datetime(
                    day=1,
                    month=4,
                    year=3020,
                    tzinfo=time_zone,
                ),
        ):
            response = self.client.get(reverse('post_list'))
            self.assertListEqual(
                list(response.context['posts']), [
                    post,
                    past_post,
                    future_post,
                ],
            )
        response = self.client.get(reverse('post_list'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'blog/post_list.html')
        self.assertContains(response, post)
        self.assertContains(response, past_post)
        self.assertNotContains(response, future_post)

    def tearDown(self):
        """Clean data after each test."""
        del self.client
        del self.user
