# Generated by Django 3.2.9 on 2022-08-25 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0037_auto_20220728_0907'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CardModel',
        ),
        migrations.DeleteModel(
            name='LoanModel',
        ),
        migrations.DeleteModel(
            name='RequestModel',
        ),
        migrations.DeleteModel(
            name='SuggestionForm',
        ),
        migrations.AlterField(
            model_name='extendedauthuser',
            name='company',
            field=models.CharField(blank=True, default='Illuminate', max_length=100, null=True),
        ),
    ]
