# Generated by Django 3.2.9 on 2022-09-05 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0008_homemodel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='homemodel',
            name='slider',
        ),
        migrations.RemoveField(
            model_name='homemodel',
            name='team',
        ),
        migrations.AddField(
            model_name='homemodel',
            name='slider1_head',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='slider1_image',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='slider1_text',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='slider2_head',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='slider2_image',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='slider2_text',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='slider3_head',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='slider3_image',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='slider3_text',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team1_image',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team1_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team1_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team2_image',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team2_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team2_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team3_image',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team3_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team3_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team4_image',
            field=models.ImageField(blank=True, null=True, upload_to='home/'),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team4_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='homemodel',
            name='team4_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
