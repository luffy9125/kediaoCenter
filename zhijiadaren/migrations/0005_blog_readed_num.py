# Generated by Django 2.0 on 2019-08-31 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zhijiadaren', '0004_auto_20190831_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='readed_num',
            field=models.IntegerField(default=0),
        ),
    ]