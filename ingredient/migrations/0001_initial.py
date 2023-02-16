# Generated by Django 4.1.3 on 2023-02-16 00:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="OwnIngredientCategory",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=64)),
            ],
            options={
                "verbose_name": "own_ingredients_category",
                "verbose_name_plural": "own_ingredients_category",
                "db_table": "own_ingredients_category",
            },
        ),
        migrations.CreateModel(
            name="OwnIngredients",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("type", models.CharField(max_length=64)),
                ("name", models.CharField(max_length=64)),
                ("amount", models.FloatField()),
                (
                    "unit",
                    models.CharField(
                        choices=[
                            ("kilogram", "Kilogram"),
                            ("gram", "Gram"),
                            ("ounce", "Ounce"),
                            ("pound", "Pound"),
                        ],
                        max_length=12,
                    ),
                ),
                ("expiration_date", models.DateField()),
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="ingredient.owningredientcategory",
                    ),
                ),
            ],
            options={
                "verbose_name": "own_ingredients",
                "verbose_name_plural": "own_ingredients",
                "db_table": "own_ingredients_info",
            },
        ),
    ]
