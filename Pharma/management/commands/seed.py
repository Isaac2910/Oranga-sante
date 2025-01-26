from django.core.management.base import BaseCommand
from Pharma.models import Categorie, Produit, Commande, CommandeProduit
from django.contrib.auth.models import User
from faker import Faker
import random
from io import BytesIO
from django.core.files import File
import qrcode
from django.db import connection

def reset_autoincrement():
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="Pharma_commande";')

class Command(BaseCommand):
    help = 'Seed the database with fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Supprimer les anciennes données dans le bon ordre
        CommandeProduit.objects.all().delete()  # Supprimer les produits liés aux commandes d'abord
        Commande.objects.all().delete()
        Produit.objects.all().delete()
        Categorie.objects.all().delete()
        User.objects.all().delete()

        # Réinitialiser le compteur d'ID pour éviter les conflits
        reset_autoincrement()

        # Créer des utilisateurs fictifs (clients)
        users = []
        for _ in range(5):
            user = User.objects.create_user(
                username=fake.user_name(),
                password=fake.password(),
                email=fake.email()
            )
            users.append(user)

        # Créer des catégories fictives
        categories = []
        for _ in range(3):
            category = Categorie.objects.create(name=fake.word())
            categories.append(category)

        # Créer des produits fictifs
        produits = []
        for _ in range(10):
            produit = Produit.objects.create(
                name=fake.word(),
                prix=random.randint(10, 1000),
                description=fake.text(),
                stock=random.randint(1, 100),
                requiert_ordonnance=random.choice([True, False]),
                categorie=random.choice(categories)
            )
            produits.append(produit)

        # Créer des commandes fictives
        commandes = []
        for _ in range(5):
            user = random.choice(users)
            commande = Commande.objects.create(
                client=user,
                montant_total=random.randint(100, 1000),
                total=random.random() * 100,
                assurance=random.choice([True, False]),
                statut=random.choice(['en_attente', 'en_cours', 'terminee', 'annulee'])
            )
            commandes.append(commande)

            # Créer un QR code pour la commande
            self.create_qr_code(commande)

            # Ajouter des produits à la commande
            for _ in range(random.randint(1, 3)):  # Ajouter 1 à 3 produits par commande
                produit = random.choice(produits)
                quantity = random.randint(1, 5)
                CommandeProduit.objects.create(
                    commande=commande,
                    produit=produit,
                    quantity=quantity
                )

        self.stdout.write(self.style.SUCCESS('Base de données peuplée avec des données fictives!'))

    def create_qr_code(self, commande):
        """Génère un QR code pour une commande."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = f"Commande ID:{commande.id}, Client:{commande.client.username}, Montant:{commande.total}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')

        buffer = BytesIO()
        img.save(buffer)
        filename = f"commande_{commande.id}_qr.png"
        commande.qr_code.save(filename, File(buffer), save=False)
        commande.save()
