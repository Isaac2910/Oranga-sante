from django.contrib import admin
from .models import Categorie, Produit, Commande, CommandeProduit
from django.utils.html import format_html
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html
from .models import Commande

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


class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'statut')
    actions = ['scan_qr_code']

    def scan_qr_code(self, request, queryset):
        """
        Redirige l'administrateur vers une page où il peut scanner un QR code.
        """
        return redirect('admin:scan_qr_page')

    scan_qr_code.short_description = "Scanner un QR code"

    def qr_code_display(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="100" height="100" />', obj.qr_code.url)
        return "Aucun QR Code"
    qr_code_display.short_description = "QR Code"

    # Ajouter une URL personnalisée dans l'admin
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('scan/', self.admin_site.admin_view(self.scan_qr_page), name='scan_qr_page'),
        ]
        return custom_urls + urls

    def scan_qr_page(self, request):
        """
        Vue pour scanner le QR code.
        """
        if request.method == "POST":
            # Récupérer l'ID de commande scanné
            commande_id = request.POST.get('commande_id')
            try:
                commande = Commande.objects.get(id=commande_id)
                commande.statut = 'terminee'  # Change le statut à "Terminée"
                commande.save()
                self.message_user(request, f"La commande {commande_id} a été validée.")
                return redirect('..')  # Retourne à la liste des commandes
            except Commande.DoesNotExist:
                self.message_user(request, f"Commande {commande_id} introuvable.", level='error')

        return render(request, 'admin/scan_qr_code.html')

admin.site.register(Commande, CommandeAdmin)