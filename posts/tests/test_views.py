from django.core.paginator import Paginator
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import override_settings

import tempfile

from posts.models import Follow, Post
from posts.forms import PostForm
from posts.tests.base_class import PostBaseTestClass


class PostsViewsTest(PostBaseTestClass):

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts',
                                  kwargs={'slug': 'testgroup'}),
            'new_post.html': reverse('new_post')
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_and_group_posts_pass_correct_contexts(self):
        views = {'index': None, 'group_posts': {'slug': 'testgroup'}}
        for view_name, kwargs in views.items():
            response = self.authorized_client.get(
                reverse(view_name, kwargs=kwargs))
            group = response.context.get('group', None)
            paginator = response.context.get('paginator')
            if group is not None:
                self.assertEqual(group, PostsViewsTest.group)
            self.assertEqual(response.context.get('page')[0], self.post)
            self.assertEqual(paginator.count, 1)
            self.assertIsInstance(paginator, Paginator)

    def test_new_post_passes_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)

    def test_group_post_appears_on_homepage(self):
        response = self.authorized_client.get(reverse('index'))
        group_post = response.context.get('page')[0]
        self.assertEqual(group_post, self.post)

    def test_group_post_appears_on_group_page(self):
        response = self.authorized_client.get(
                reverse('group_posts', kwargs={'slug': 'testgroup'}))
        group_post = response.context.get('page')[0]
        self.assertEqual(group_post, self.post)

    def test_post_does_not_appear_in_other_group(self):
        response = self.authorized_client.get(
                reverse('group_posts', kwargs={'slug': 'testgroup2'}))
        group_posts = response.context.get('page')
        self.assertTrue(self.post not in group_posts)

    def test_post_edit_passes_correct_context(self):
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={'username': 'testsubject',
                                         'post_id': 1}))
        author = response.context.get('author')
        post = response.context.get('post')
        form = response.context.get('form')
        self.assertEqual(author, self.user)
        self.assertEqual(post, self.post)
        self.assertIsInstance(form, PostForm)

    def test_profile_passes_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': 'testsubject'}))
        author = response.context.get('author')
        post = response.context.get('page')[0]
        paginator = response.context.get('paginator')
        self.assertEqual(author, self.user)
        self.assertEqual(post, self.post)
        self.assertIsInstance(paginator, Paginator)

    def test_post_view_passes_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': 'testsubject',
                                    'post_id': 1}))
        author = response.context.get('author')
        post = response.context.get('post')
        comment = response.context.get('comments')[0]
        self.assertEqual(author, self.user)
        self.assertEqual(post, self.post)
        self.assertEqual(comment, self.comment)

    def test_about_author_and_about_spec_pass_correct_contexts(self):
        views = {
            reverse('about-author'):
                ['About me', 'Well, we will think of that later.'],
            reverse('about-spec'):
                ['Technologies used', 'Still not a single idea.'],
        }
        for view_name, value in views.items():
            response = self.authorized_client.get(view_name)
            self.assertEqual(
                response.context.get('flatpage').title, value[0])
            self.assertEqual(
                response.context.get('flatpage').content, value[1])

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_images(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Trying out some images.',
            'group': 1,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        urls = [
            reverse('index'),
            reverse('profile', kwargs={'username': 'testsubject'}),
            reverse('group_posts', kwargs={'slug': 'testgroup'})
        ]
        for url in urls:
            cache.clear()
            response = self.authorized_client.get(url)
            with self.subTest():
                self.assertNotEqual(
                    response.context.get('page')[0].image, None
                )
        response = self.authorized_client.get(
            reverse('post', kwargs={'username': 'testsubject', 'post_id': 2})
        )
        self.assertNotEqual(response.context.get('post').image, None)

    def test_cached_index_works_properly(self):
        page_before = self.authorized_client.get(reverse('index')).content
        self.authorized_client.post(
            reverse('new_post'),
            data={
                'text': 'Pathetic attempts to create a masterpiece.',
                'group': 2,
            }
        )
        page_after = self.authorized_client.get(reverse('index')).content
        self.assertEqual(page_before, page_after)
        cache.clear()
        page_after = self.authorized_client.get(reverse('index')).content
        self.assertNotEqual(page_before, page_after)

    def test_user_can_subscribe_and_unsubscribe(self):
        follows_before = Follow.objects.count()
        response1 = self.not_author.get(
            reverse('profile_follow', kwargs={'username': 'testsubject'})
        )
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(Follow.objects.count(), follows_before+1)
        response2 = self.not_author.get(
            reverse('profile_unfollow', kwargs={'username': 'testsubject'})
        )
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(Follow.objects.count(), follows_before)

    def test_new_post_is_appears_on_follow_for_subscribers(self):
        self.not_author.get(
            reverse('profile_follow', kwargs={'username': 'testsubject'})
        )
        self.authorized_client.post(
            reverse('new_post'),
            data={
                'text': 'I hope this will work out well.',
                'group': 2,
            }
        )
        response1 = self.not_author.get(reverse('follow_index'))
        response2 = self.authorized_client.get(reverse('follow_index'))
        self.assertEqual(response1.context.get('page')[0].id, 2)
        self.assertEqual(response2.context.get('paginator').count, 0)
