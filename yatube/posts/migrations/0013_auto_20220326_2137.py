# Generated by Django 2.2.16 on 2022-03-26 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_auto_20220326_1904'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_follow'),
        ),
    ]
