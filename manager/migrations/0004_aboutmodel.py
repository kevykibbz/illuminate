# Generated by Django 3.2.9 on 2022-09-04 12:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('manager', '0003_servicemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('h1', models.CharField(blank=True, max_length=100, null=True)),
                ('h1_text', models.TextField(blank=True, max_length=100, null=True)),
                ('h2', models.CharField(blank=True, max_length=100, null=True)),
                ('h2_text', models.TextField(blank=True, max_length=100, null=True)),
                ('h2_image', models.ImageField(blank=True, null=True, upload_to='about/')),
                ('h3', models.CharField(blank=True, max_length=100, null=True)),
                ('h3_text', models.TextField(blank=True, max_length=100, null=True)),
                ('h3_image', models.ImageField(blank=True, null=True, upload_to='about/')),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'about_tbl',
                'db_table': 'about_tbl',
            },
        ),
    ]
