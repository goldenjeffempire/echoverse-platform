# Generated by Django 5.1.3 on 2024-11-07 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Echoverse', '0010_alter_comment_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
