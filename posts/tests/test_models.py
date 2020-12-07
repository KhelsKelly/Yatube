from posts.tests.base_class import PostBaseTestClass


class PostModelTest(PostBaseTestClass):

    def test_post_verbose_name(self):
        post = self.post
        field_verboses = {
            'text': 'Содержание записи',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
            'image': 'Изображение',
        }
        for field, expected in field_verboses.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected)

    def test_post_help_text(self):
        post = self.post
        field_help_texts = {
            'text': 'Вложите в этот пост всю свою душу, но без выражений!',
            'group': 'Выберите группу, в которой будет опубликована запись.',
            'image': 'Можете прикрепить сюда свою фотографию.',
        }
        for field, expected in field_help_texts.items():
            with self.subTest():
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected)

    def test_str_post(self):
        post = self.post
        post_expected_name = post.text[:15]
        self.assertEqual(str(post), post_expected_name)

    def test_str_group(self):
        group = self.group
        group_expected_name = group.title
        self.assertEqual(str(group), group_expected_name)

    def test_str_comment(self):
        comment = self.comment
        comment_expected_name = comment.text[:15]
        self.assertEqual(str(comment), comment_expected_name)
