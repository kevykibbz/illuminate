# Generated by Django 3.2.9 on 2022-07-10 08:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0015_auto_20220710_1113'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuggestionForm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True, verbose_name='name')),
                ('email', models.CharField(blank=True, help_text='email address', max_length=50, null=True, verbose_name='email address')),
                ('city', models.CharField(blank=True, help_text='city', max_length=100, null=True, verbose_name='city')),
                ('state', models.CharField(blank=True, help_text='state', max_length=100, null=True, verbose_name='state')),
                ('suggestion', models.TextField(blank=True, null=True)),
                ('isread', models.IntegerField(blank=True, default=0, null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name_plural': 'suggestions',
                'db_table': 'suggestions',
            },
        ),
    ]
