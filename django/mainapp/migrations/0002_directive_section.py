# Generated by Django 3.1.1 on 2021-02-28 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='directive',
            name='section',
            field=models.CharField(max_length=100, null=True),
        ),
    ]