# Generated by Django 5.1.5 on 2025-01-30 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pharma', '0004_alter_produit_categorie'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commande',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
    ]
