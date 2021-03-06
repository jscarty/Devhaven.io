# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-17 18:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0016_auto_20160412_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='field',
            field=models.CharField(choices=[('Hardware and OS', 'Hardware and OS'), ('Desktops', 'Desktops'), ('Tablets', 'Tablets'), ('Phones', 'Phones'), ('Wearables', 'Wearables'), ('Windows', 'Windows'), ('Mac OS X', 'Mac OS X'), ('Linux and Unix', 'Linux and Unix'), ('Programming and Computer Science', 'Programming and Computer Science'), ('Software Development', 'Software Development'), ('Web Development (Front)', 'Web Development (Front)'), ('Web Development (Back)', 'Web Development (Back)'), ('Mobile Development', 'Mobile Development'), ('Game Development', 'Game Development'), ('Algorithms and Data Structures', 'Algorithms and Data Structures'), ('Databases', 'Databases'), ('IDE / Text Editors', 'IDE / Text Editors'), ('Tutorial', 'Tutorial'), ('Opinion', 'Opinion'), ('Miscellaneous', 'Miscellaneous')], default='Unspecified', max_length=200),
        ),
        migrations.AlterField(
            model_name='post',
            name='title',
            field=models.CharField(max_length=150),
        ),
    ]
