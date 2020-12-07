import shutil
import tempfile
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Comment, Group, Post, User
from posts.forms import PostForm


class PostBaseTestClass(TestCase):
    """Base class containing all the necessary data and objects for tests."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.group = Group.objects.create(
            title='testgroup',
            slug='testgroup',
            description='It is nothing but a mere testgroup.',
        )
        cls.group2 = Group.objects.create(
            title='testgroup2',
            slug='testgroup2',
            description='It is nothing but a mere testgroup2.',
        )
        cls.site = Site.objects.get(pk=1)
        cls.flatpage_author = FlatPage.objects.create(
            url='/about-author/',
            title='About me',
            content='Well, we will think of that later.'
        )
        cls.flatpage_spec = FlatPage.objects.create(
            url='/about-spec/',
            title='Technologies used',
            content='Still not a single idea.'
        )
        cls.flatpage_author.sites.add(cls.site)
        cls.flatpage_spec.sites.add(cls.site)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create(username='testsubject')
        self.impostor = User.objects.create(username='impostor')
        self.authorized_client = Client()
        self.not_author = Client()
        self.authorized_client.force_login(self.user)
        self.not_author.force_login(self.impostor)
        self.post = Post.objects.create(
            text='Just a meaningless set of words.',
            author=self.user,
            group=self.group,
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            text='I have high expectations of you, comment.',
        )
        self.form = PostForm()
        cache.clear()
