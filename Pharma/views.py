# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Produit, Commande, CommandeProduit, Categorie
import json

# --- Produits ---
def liste_produits(request):
    produits = Produit.objects.all()
    data = [
        {
            "id": produit.id,
            "name": produit.name,
            "url_image": produit.url_image,
            "prix": produit.prix,
            "description": produit.description,
            "stock": produit.stock,
            "requiert_ordonnance": produit.requiert_ordonnance,
            "categorie": produit.categorie.name,
        }
        for produit in produits
    ]
    return JsonResponse(data, safe=False)


def detail_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    data = {
        "id": produit.id,
        "name": produit.name,
        "url_image": produit.url_image,
        "prix": produit.prix,
        "description": produit.description,
        "stock": produit.stock,
        "requiert_ordonnance": produit.requiert_ordonnance,
        "categorie": produit.categorie.name,
    }
    return JsonResponse(data)


# --- Panier ---
def afficher_panier(request):
    panier = request.session.get('panier', {})
    items = []
    total = 0

    for produit_id, quantity in panier.items():
        produit = get_object_or_404(Produit, id=produit_id)
        items.append({
            "id": produit.id,
            "name": produit.name,
            "prix": produit.prix,
            "quantity": quantity,
            "subtotal": produit.prix * quantity,
        })
        total += produit.prix * quantity

    data = {
        "items": items,
        "total": total,
    }
    return JsonResponse(data)


def ajouter_au_panier(request, produit_id):
    if request.method == "POST":
        produit = get_object_or_404(Produit, id=produit_id)
        quantity = int(request.POST.get('quantity', 1))

        if quantity > produit.stock:
            return JsonResponse({
                "error": f"Stock insuffisant pour {produit.name}. Disponible: {produit.stock}."
            }, status=400)

        panier = request.session.get('panier', {})
        panier[produit_id] = panier.get(produit_id, 0) + quantity

        if panier[produit_id] > produit.stock:
            return JsonResponse({
                "error": f"Quantité totale demandée dépasse le stock disponible pour {produit.name}."
            }, status=400)

        request.session['panier'] = panier
        request.session.modified = True

        return JsonResponse({"message": f"{produit.name} ajouté au panier."})

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)


def vider_panier(request):
    if request.method == "POST":
        request.session['panier'] = {}
        request.session.modified = True
        return JsonResponse({"message": "Panier vidé avec succès."})

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)


# --- Commandes ---


@login_required
@csrf_exempt
def creer_commande(request):
    if request.method == 'POST':
        # Récupérer les données JSON
        produits = json.loads(request.POST.get('produits', '[]'))
        assurance = request.POST.get('assurance', False) == 'true'

        # Créer la commande
        commande = Commande.objects.create(client=request.user, assurance=assurance)

        # Traiter les produits
        for item in produits:
            produit = get_object_or_404(Produit, id=item['id'])
            quantity = int(item['quantity'])
            if quantity > produit.stock:
                return JsonResponse({
                    "error": f"Stock insuffisant pour le produit {produit.name}. Disponible: {produit.stock}."
                }, status=400)
            CommandeProduit.objects.create(commande=commande, produit=produit, quantity=quantity)

        # Calculer le montant total
        commande.montant_total = commande.calculer_montant_total()

        # Gestion de l'ordonnance
        if 'ordonnance' in request.FILES:
            commande.ordonnance = request.FILES['ordonnance']

        commande.save()

        return JsonResponse({
            "message": "Commande créée avec succès.",
            "commande_id": commande.id,
        })

    return JsonResponse({"error": "Méthode non autorisée."}, status=405)



@login_required
def detail_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)
    data = {
        "id": commande.id,
        "date_commande": commande.date_commande,
        "statut": commande.statut,
        "montant_total": commande.montant_total,
        "assurance": commande.assurance,
        "produits": [
            {
                "id": item.produit.id,
                "name": item.produit.name,
                "quantity": item.quantity,
                "prix": item.produit.prix,
            }
            for item in commande.commande_produits.all()
        ],
        "qr_code_url": commande.qr_code.url if commande.qr_code else None,
    }
    return JsonResponse(data)
