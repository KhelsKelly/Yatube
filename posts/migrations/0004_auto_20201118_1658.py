# Generated by Django 2.2.6 on 2020-11-18 13:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20201025_0528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Выберите группу, в которой будет опубликована запись.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Группа'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Вложите в этот пост всю свою душу, но без выражений!', verbose_name='Содержание записи'),
        ),
    ]
