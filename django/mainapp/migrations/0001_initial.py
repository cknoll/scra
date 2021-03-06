# Generated by Django 3.1.1 on 2021-02-28 17:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Directive",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=1000, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="SourceDocument",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=1000, null=True)),
                ("source_uri", models.CharField(max_length=1000, null=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="GeographicEntity",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=1000, null=True)),
                ("applying_direcitves", models.ManyToManyField(to="mainapp.Directive")),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="directive",
            name="source_document",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="mainapp.sourcedocument"),
        ),
    ]
