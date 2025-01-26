import random
from faker import Faker
from django.core.management.base import BaseCommand
from Pharma.models import Article

class Command(BaseCommand):
    help = "Génère des articles fictifs pour la base de données."

    def add_arguments(self, parser):
        parser.add_argument(
            'count',
            type=int,
            help="Nombre d'articles à générer.",
        )

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        fake = Faker('fr_FR')  # Générer des données en français
        
        for _ in range(count):
            titre = fake.sentence(nb_words=6)
            contenu = fake.paragraph(nb_sentences=10)
            image_path = random.choice([
                "articles/exemple1.jpg",
                "articles/exemple2.jpg",
                "articles/exemple3.jpg",
            ])  # Assurez-vous que ces fichiers existent dans votre dossier media/articles/
            
            Article.objects.create(
                titre=titre,
                contenu=contenu,
                image=image_path
            )
        
        self.stdout.write(self.style.SUCCESS(f"{count} articles générés avec succès !"))
