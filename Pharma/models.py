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
    url_image = models.URLField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    stock = models.PositiveIntegerField()  # Stock ne peut pas être négatif
    requiert_ordonnance = models.BooleanField(default=False)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(stock__gte=0), name='stock_positive'),
        ]

    def __str__(self):
        return self.name


class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    assurance = models.BooleanField(default=False)
    ordonnance = models.FileField(upload_to='ordonnances/', blank=True, null=True) 
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Génération du QR code après avoir sauvegardé pour obtenir un ID
        if not self.pk:
            super().save(*args, **kwargs)

        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f"Commande ID:{self.id}, Client:{self.client.username}, Montant:{self.montant_total}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')

            buffer = BytesIO()
            img.save(buffer)
            filename = f"commande_{self.id}_qr.png"
            self.qr_code.save(filename, File(buffer), save=False)

        super().save(*args, **kwargs)

    def calculer_montant_total(self):
        return sum(item.produit.prix * item.quantity for item in self.commande_produits.all())

    def __str__(self):
        return f"Commande {self.id} - {self.client.username}"


class CommandeProduit(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='commande_produits')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.quantity > self.produit.stock:
            raise ValueError(f"Quantité demandée ({self.quantity}) dépasse le stock disponible ({self.produit.stock}).")
        # Met à jour le stock après validation
        self.produit.stock -= self.quantity
        self.produit.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.name} x{self.quantity} dans commande {self.commande.id}"
