from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    class Meta:
        ordering = ['-pub_date']

    text = models.TextField(verbose_name='Содержание записи',
                            help_text='Вложите в этот пост всю '
                            'свою душу, но без выражений!')
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name='posts',
                              blank=True, null=True,
                              verbose_name='Группа',
                              help_text='Выберите группу, в которой '
                              'будет опубликована запись.')
    image = models.ImageField(upload_to='posts/', blank=True, null=True,
                              verbose_name='Изображение',
                              help_text='Можете прикрепить '
                              'сюда свою фотографию.')

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    class Meta:
        ordering = ['-created']

    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')

    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')

    text = models.TextField(verbose_name='Комментарий',
                            help_text='Выразите своё мнение'
                                      '(желательно, вежливо).')

    created = models.DateTimeField(verbose_name='Дата добавления',
                                   auto_now_add=True, db_index=True)

    def __str__(self):
        return self.text[:15]
