# Generated by Django 5.1.1 on 2025-01-23 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pharma', '0003_alter_produit_url_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commande',
            name='montant_total',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='produit',
            name='prix',
            field=models.PositiveIntegerField(),
        ),
    ]
