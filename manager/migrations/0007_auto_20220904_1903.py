# Generated by Django 3.2.9 on 2022-09-04 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0006_auto_20220904_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aboutmodel',
            name='h1',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='aboutmodel',
            name='h1_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='aboutmodel',
            name='h2',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='aboutmodel',
            name='h2_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='aboutmodel',
            name='h3_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
