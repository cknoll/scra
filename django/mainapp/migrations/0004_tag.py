# Generated by Django 3.1.1 on 2021-03-04 08:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0003_auto_20210228_2055"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=1000, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
