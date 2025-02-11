# models.py
from django.db import models
from django.conf import settings
from django.core.files import File
from io import BytesIO
import qrcode

class Categorie(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Produit(models.Model):
    name = models.CharField(max_length=100)
    url_image = models.ImageField(upload_to='produits/', blank=True, null=True)

    prix = models.PositiveIntegerField()
    description = models.TextField()
    stock = models.PositiveIntegerField()  # Stock ne peut pas être négatif
    requiert_ordonnance = models.BooleanField(default=False)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(stock__gte=0), name='stock_positive'),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/produits/{self.id}/"

    @property
    def imageURL(self):
        try:
            return self.image.url
        except:
            return ''
class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    MODES_LIVRAISON = [
        ('standard', 'Livraison standard (2h à 4h) : 3000f'),
        ('express', 'Livraison express (≤1h) : 5000f'),
        ('retrait', 'Retrait en magasin'),     

    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    montant_total = models.PositiveIntegerField(default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    mode_livraison = models.CharField(max_length=20, choices=MODES_LIVRAISON, default='standard')

    assurance = models.BooleanField(default=False)
    ordonnance = models.FileField(upload_to='ordonnances/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    
    @property
    def prix_total(self):
        total = sum(
            item.produit.prix * item.quantity
            for item in self.commande_produits.all()
        )
        return total
    

    def save(self, *args, **kwargs):
        # Sauvegarde initiale pour obtenir l'ID avant de générer le QR Code
        if not self.pk:  # Seulement si la commande n'existe pas encore
            super().save(*args, **kwargs)

            # Génération du QR code après avoir obtenu l'ID
            if not self.qr_code:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr_data = f"Commande ID:{self.id}, Client:{self.client.username}, Montant:{self.total}"
                qr.add_data(qr_data)
                qr.make(fit=True)
                img = qr.make_image(fill_color='black', back_color='white')

                buffer = BytesIO()
                img.save(buffer)
                filename = f"commande_{self.id}_qr.png"
                self.qr_code.save(filename, File(buffer), save=False)

        super().save(*args, **kwargs)

    @property
    def shipping(self):
        orderitems = self.commande_produits.all()
        for item in orderitems:
            if not item.produit.requiert_ordonnance:
                return True
        return False
    
    @property
    def produits_commandes(self):
        return ", ".join(
            f"{item.produit.name} (x{item.quantity})"
            for item in self.commande_produits.all()
        )
    
    @property
    def prix_livraison(self):
        if self.mode_livraison == 'standard':
            return 3000
        elif self.mode_livraison == 'express':
            return 5000
        elif self.mode_livraison == 'retrait':
            return 0
        return 0  # 






    def __str__(self):
        return f"Commande {self.id} - {self.client.username}"

    def get_absolute_url(self):
        return f"/commandes/{self.id}/"



class CommandeProduit(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='commande_produits')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        # Vérification de la quantité de stock avant d'ajouter le produit
        if self.quantity > self.produit.stock:
            raise ValueError(f"Quantité demandée ({self.quantity}) dépasse le stock disponible ({self.produit.stock}).")
        
        # Mise à jour du stock du produit
        self.produit.stock -= self.quantity
        try:
            self.produit.save()
        except Exception as e:
            raise ValueError(f"Erreur lors de l'enregistrement du produit: {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.name} x{self.quantity} dans commande {self.commande.id}"
    # Mise à jour du stock du produit

class Article(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_publication = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to="articles/")
    
    def __str__(self):
        return self.titre