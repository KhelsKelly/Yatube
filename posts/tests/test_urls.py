from django.urls import reverse
from django.core.cache import cache

from posts.tests.base_class import PostBaseTestClass


class StaticURLTests(PostBaseTestClass):

    def test_url_exists_at_desired_location(self):
        urls = [
            reverse('index'),
            reverse('group_posts', kwargs={'slug': 'testgroup'}),
            reverse('profile', kwargs={'username': 'testsubject'}),
            reverse('post', kwargs={'username': 'testsubject', 'post_id': 1}),
        ]
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_url_new_is_unavailable_to_unauthorized_user(self):
        response = self.guest_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 302)

    def test_url_new_is_available_to_authorized_user(self):
        response = self.authorized_client.get(reverse('new_post'))
        self.assertEqual(response.status_code, 200)

    def test_flatpage_about_author(self):
        response = self.guest_client.get(reverse('about-author'))
        self.assertEqual(response.status_code, 200)

    def test_flatpage_about_spec(self):
        response = self.guest_client.get(reverse('about-spec'))
        self.assertEqual(response.status_code, 200)

    def test_url_uses_correct_template(self):
        cache.clear()
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse(
                'group_posts', kwargs={'slug': 'testgroup'}
            ),
            'new_post.html': reverse('new_post'),
            'edit_post.html': reverse(
                'post_edit', kwargs={'username': 'testsubject', 'post_id': 1}
            ),
        }
        for template, url in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_post_edit_is_available_for_author(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={'username': 'testsubject', 'post_id': 1})
        )
        self.assertEqual(response.status_code, 200)

    def test_page_edit_post_is_unavailable_for_non_author(self):
        response = self.not_author.get(
            reverse(
                'post_edit',
                kwargs={'username': 'testsubject', 'post_id': 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_returns_404_if_not_found(self):
        response = self.guest_client.get(
            reverse(
                'profile',
                kwargs={'username': 'non-existent-user'})
        )
        self.assertEqual(response.status_code, 404)

    def test_unauthorized_user_cannot_comment(self):
        response = self.guest_client.get(
            reverse(
                'add_comment',
                kwargs={'username': 'testsubject', 'post_id': 1})
        )
        self.assertEqual(response.status_code, 302)

    def test_unauthorized_user_cannot_subscribe(self):
        response = self.guest_client.get(
            reverse(
                'profile_follow',
                kwargs={'username': 'testsubject'})
        )
        self.assertEqual(response.status_code, 302)
