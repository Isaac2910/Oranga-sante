from django.contrib import admin
from .models import Categorie, Produit, Commande, CommandeProduit


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'prix', 'stock', 'requiert_ordonnance', 'categorie')
    list_filter = ('requiert_ordonnance', 'categorie')
    search_fields = ('name', 'description')


class CommandeProduitInline(admin.TabularInline):
    model = CommandeProduit
    extra = 1  # Nombre de lignes supplémentaires dans l'interface

from django.contrib import admin
from django.shortcuts import render, get_object_or_404
from django.urls import path
from .models import Categorie, Produit, Commande, CommandeProduit


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date_commande', 'montant_total', 'statut', 'assurance')
    list_filter = ('statut', 'assurance', 'date_commande')
    search_fields = ('client__username',)
    actions = ['valider_commandes']

    # Action personnalisée pour valider les commandes sélectionnées
    def valider_commandes(self, request, queryset):
        queryset.update(statut='terminee')
        self.message_user(request, "Les commandes sélectionnées ont été validées.")
    valider_commandes.short_description = "Valider les commandes sélectionnées"

    # Ajout d'une URL personnalisée
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('scan_qr/', self.admin_site.admin_view(self.scan_qr), name='scan_qr'),
        ]
        return custom_urls + urls

    # Méthode pour scanner et valider une commande via un QR code
    def scan_qr(self, request):
        if request.method == "POST":
            qr_code_data = request.POST.get('qr_code_data')
            if not qr_code_data:
                self.message_user(request, "Aucun QR code détecté.", level="error")
                return render(request, 'admin/scan_qr.html')

            # Extraction de l'ID de la commande depuis les données du QR code
            try:
                commande_id = int(qr_code_data.split("ID:")[1].split(",")[0])
                commande = get_object_or_404(Commande, id=commande_id)
                commande.statut = 'terminee'
                commande.save()
                self.message_user(request, f"Commande {commande_id} validée avec succès.")
            except (IndexError, ValueError):
                self.message_user(request, "Données du QR code invalides.", level="error")
            except Commande.DoesNotExist:
                self.message_user(request, "Commande introuvable.", level="error")

        return render(request, 'admin/scan_qr.html')
