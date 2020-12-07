from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

import tempfile

from posts.models import Post, Comment
from posts.tests.base_class import PostBaseTestClass


class PostsFormsTest(PostBaseTestClass):

    def test_new_form_creates_new_record_in_db(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Pathetic attempts to create a masterpiece.',
            'group': 2,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
        )
        last_post = Post.objects.first()
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group, PostsFormsTest.group2)
        self.assertEqual(Post.objects.count(), posts_count+1)

    def test_post_edit_changes_post_model_through_form(self):
        form_data = {
            'text': 'First I change this post and second...',
            'group': 2
        }
        self.authorized_client.post(
            reverse('post_edit', kwargs={'username': 'testsubject',
                                         'post_id': 1}),
            data=form_data,
        )
        post = Post.objects.first()
        self.assertEqual(post.text, 'First I change this post and second...')
        self.assertEqual(post.group, PostsFormsTest.group2)
        self.assertTrue(Post.objects.count() == 1)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_new_post_creates_post_with_image(self):
        posts_count = Post.objects.count()
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
            'group': 2,
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count+1)

    def test_add_comment_creates_correct_record_in_db(self):
        comments_before = Comment.objects.count()
        form_data = {
            'text': 'I have high expectations of you, comment.',
        }
        self.authorized_client.post(
            reverse('add_comment', kwargs={'username': 'testsubject',
                                           'post_id': 1}),
            data=form_data,
            follow=True
        )
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), comments_before+1)
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
