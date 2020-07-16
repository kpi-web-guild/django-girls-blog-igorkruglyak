"""Tests for models."""
from unittest.mock import patch
from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from blog.models import Post


class ModelPostTest(TestCase):
    """Class for testing Post models of this project."""

    def setUp(self):
        """Prepare data for testing."""
        self.user = User.objects.create(username='testuser')
        self.test_post = (
            Post.objects.create(
                author=self.
                user, title='Test', text='superText',
            )
        )

    def test_post_rendering(self):
        """Post is rendered as its title."""
        self.assertEqual(str(self.test_post), self.test_post.title)

    @patch(
        'django.utils.timezone.now',
        lambda: datetime(
            day=1, month=4, year=2020,
            tzinfo=timezone.get_current_timezone(),
        ),
    )
    def test_post_publish_method(self):
        """Publish method working ok."""
        self.test_post.publish()
        self.assertEqual(
            self.test_post.published_date, datetime(
                day=27, month=6, year=2020,
                tzinfo=timezone.get_current_timezone(),
            ),
        )

    def tearDown(self):
        """Clean data for new test."""
        del self.user
        del self.test_post
