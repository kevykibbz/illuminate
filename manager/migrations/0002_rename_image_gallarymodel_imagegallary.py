# Generated by Django 3.2.9 on 2022-09-04 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='gallarymodel',
            old_name='image',
            new_name='imagegallary',
        ),
    ]