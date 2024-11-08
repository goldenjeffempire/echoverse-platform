# Generated by Django 5.1.2 on 2024-11-04 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Echoverse', '0005_like'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='text',
            new_name='content',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pictures/'),
        ),
    ]
