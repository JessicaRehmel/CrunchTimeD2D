# Generated by Django 2.2.6 on 2020-02-10 22:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TestBookStore', '0003_remove_author_authorid'),
    ]

    operations = [
        migrations.DeleteModel(
            name='OnixFile',
        ),
    ]
