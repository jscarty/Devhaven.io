# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-23 07:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0003_auto_20160322_2359'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsletterSignUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=130, null=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.DeleteModel(
            name='SignUp',
        ),
    ]
