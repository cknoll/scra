# Generated by Django 3.1.1 on 2021-03-04 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0004_tag"),
    ]

    operations = [
        migrations.AddField(
            model_name="directive",
            name="tags",
            field=models.ManyToManyField(to="mainapp.Tag"),
        ),
    ]