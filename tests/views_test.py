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

    def test_detail_view(self):
        """Testing detail page when post is not exist and when it exists."""
        response = self.client.get(reverse('post_detail', kwargs={'pk': 1}))
        self.assertEqual(404, response.status_code)
        post = Post.objects.create(
            author=self.user, title='Test',
            text='superText',
        )
        response = self.client.get(
            reverse(
                'post_detail', kwargs={
                    'pk':
                    post.pk,
                },
            ),
        )
        self.assertEqual(200, response.status_code)

    def test_post_new_view(self):
        """Testing new post view before and after login."""
        response = self.client.get(reverse('post_new'))
        self.assertEqual(302, response.status_code)
        authorization = self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )
        self.assertTrue(authorization)
        response = self.client.post(
            reverse('post_new'), {
                'author': self.user,
                'title': 'Test',
                'text': 'superText',
            }, follow=True,
        )
        self.assertEqual(200, response.status_code)
        self.assertRedirects(
            response, reverse(
                'post_detail', kwargs={
                    'pk':
                    1,
                },
            ),
        )

    def test_post_edit(self):
        """Testing edit views before and after user login."""
        response = self.client.get(reverse('post_edit', kwargs={'pk': 1}))
        self.assertEqual(302, response.status_code)
        authorization = self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )
        self.assertTrue(authorization)
        response = self.client.get(reverse('post_edit', kwargs={'pk': 1}))
        # This time we'are logged but post is not exist
        self.assertEqual(404, response.status_code)
        post = Post.objects.create(
            author=self.user, title='Test',
            text='superText',
        )
        response = self.client.get(
            reverse(
                'post_edit', kwargs={
                    'pk':
                    post.pk,
                },
            ),
        )
        self.assertEqual(200, response.status_code)

    def test_drafts(self):
        """Testing drafts view before and after login."""
        response = self.client.get(reverse('post_draft_list'))
        self.assertEqual(302, response.status_code)
        authorization = self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )
        self.assertTrue(authorization)
        response = self.client.get(reverse('post_draft_list'))
        self.assertEqual(200, response.status_code)

    def test_publish_post(self):
        """Testing publishing post before login and after."""
        response = self.client.get(reverse('post_publish', kwargs={'pk': 1}))
        self.assertEqual(302, response.status_code)
        authorization = self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )
        self.assertTrue(authorization)
        response = self.client.get(reverse('post_publish', kwargs={'pk': 1}))
        self.assertEqual(404, response.status_code)
        post = Post.objects.create(
            author=self.user, title='Test',
            text='superText',
        )
        response = self.client.get(
            reverse(
                'post_publish', kwargs={
                    'pk':
                    post.pk,
                },
            ),
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                'post_detail', kwargs={
                    'pk':
                    post.pk,
                },
            ),
        )

    def test_delete_post(self):
        """Testing deleting post before and after login."""
        response = self.client.get(reverse('post_remove', kwargs={'pk': 1}))
        self.assertEqual(302, response.status_code)
        authorization = self.client.login(
            username=self.USERNAME,
            password=self.PASSWORD,
        )
        self.assertTrue(authorization)
        response = self.client.get(reverse('post_remove', kwargs={'pk': 1}))
        self.assertEqual(404, response.status_code)
        post = Post.objects.create(
            author=self.user, title='Test',
            text='superText',
        )
        response = self.client.post(
            reverse(
                'post_remove', kwargs={
                    'pk':
                    post.pk,
                },
            ),
            follow=True,
        )
        self.assertRedirects(response, reverse('post_list'))

    def tearDown(self):
        """Clean data after each test."""
        del self.client
        del self.user
