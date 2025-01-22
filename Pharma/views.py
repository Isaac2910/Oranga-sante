from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Produit, Commande, CommandeProduit

@login_required
def ajouter_au_panier(request, produit_id):
    """
    Ajoute un produit au panier ou met à jour la quantité dans une commande existante.
    """
    produit = get_object_or_404(Produit, id=produit_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > produit.stock:
        return JsonResponse({"error": f"Quantité demandée ({quantity}) dépasse le stock disponible ({produit.stock})."})

    # Récupérer ou créer une commande en attente pour l'utilisateur
    commande, created = Commande.objects.get_or_create(client=request.user, statut='en_attente')

    # Ajouter ou mettre à jour un produit dans la commande
    commande_produit, created = CommandeProduit.objects.get_or_create(
        commande=commande,
        produit=produit,
        defaults={'quantity': quantity}
    )
    if not created:
        commande_produit.quantity += quantity
        if commande_produit.quantity > produit.stock:
            return JsonResponse({"error": f"Quantité demandée ({commande_produit.quantity}) dépasse le stock disponible ({produit.stock})."})
        commande_produit.save()

    # Recalculer le montant total
    commande.montant_total = commande.calculer_montant_total()
    commande.save()

    return redirect('panier')

@login_required
def panier(request):
    """
    Affiche le panier de l'utilisateur avec les produits ajoutés.
    """
    commande = Commande.objects.filter(client=request.user, statut='en_attente').first()
    context = {'commande': commande}
    return render(request, 'panier.html', context)

@login_required
def payer(request):
    """
    Gère le paiement de la commande et génère un QR code.
    """
    commande = Commande.objects.filter(client=request.user, statut='en_attente').first()
    if not commande:
        return redirect('panier')

    # Simuler le paiement
    commande.statut = 'en_cours'
    commande.save()

    return render(request, 'confirmation.html', {'commande': commande})

@login_required
def historique(request):
    """
    Affiche l'historique des commandes de l'utilisateur.
    """
    commandes = Commande.objects.filter(client=request.user).exclude(statut='en_attente')
    context = {'commandes': commandes}
    return render(request, 'historique.html', context)


from django.shortcuts import render
from .models import Produit

def produits(request):
    """
    Affiche tous les produits disponibles.
    """
    produits = Produit.objects.all()
    context = {'produits': produits}
    return render(request, 'produits.html', context)
