# Generated by Django 3.2.9 on 2022-09-04 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0005_auto_20220904_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aboutmodel',
            name='h1',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='aboutmodel',
            name='h1_text',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='aboutmodel',
            name='h2',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='aboutmodel',
            name='h2_text',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='aboutmodel',
            name='h3_text',
            field=models.TextField(null=True),
        ),
    ]
