# Generated by Django 5.1.7 on 2025-03-15 18:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app01", "0009_alter_books_rate"),
    ]

    operations = [
        migrations.AlterField(
            model_name="books",
            name="people_count",
            field=models.PositiveIntegerField(default=1, verbose_name="评分人数"),
        ),
    ]
