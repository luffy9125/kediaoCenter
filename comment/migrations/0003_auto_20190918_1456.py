# Generated by Django 2.0 on 2019-09-18 06:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('comment', '0002_auto_20190918_1455'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reply',
            name='comment',
        ),
        migrations.DeleteModel(
            name='Reply',
        ),
    ]
