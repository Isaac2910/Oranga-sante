from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Produit, Commande, CommandeProduit
from django.db import transaction
#from .forms import CommandeForm  # À créer pour la commande
import qrcode
from io import BytesIO
from django.core.files import File
import json
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def page(request):
    return render(request, 'lading/base.html')
    


# Afficher tous les produits
@login_required
def produit_list(request):
    produits = Produit.objects.all()
    return render(request, 'pharma/accueil.html', {'produits': produits})

@login_required
def ajouter_au_panier(request, produit_id):
    if request.method == 'POST':
        produit = get_object_or_404(Produit, id=produit_id)
        panier = request.session.get('panier', {})

        # Obtenir la quantité demandée (par défaut : 1)
        try:
            quantite = int(request.POST.get('quantite', 1))
            if quantite <= 0:
                return JsonResponse({'success': False, 'message': "La quantité doit être supérieure à zéro."}, status=400)
        except ValueError:
            return JsonResponse({'success': False, 'message': "Quantité invalide."}, status=400)

        # Vérifier le stock disponible
        if produit.stock is not None and produit.stock < quantite:
            return JsonResponse({'success': False, 'message': "Stock insuffisant."}, status=400)

        # Ajouter ou mettre à jour l'article dans le panier
        if str(produit_id) in panier:
            panier[str(produit_id)]['quantite'] += quantite
        else:
            panier[str(produit_id)] = {
                'name': produit.name,
                'prix': produit.prix,  # Enlever la conversion en str, il est préférable de laisser comme float
                'quantite': quantite,
            }

        request.session['panier'] = panier

        # Calcul du total
        total = sum(item['prix'] * item['quantite'] for item in panier.values())  # Plus besoin de float ici, prix est déjà un float

        return JsonResponse({
            'success': True,
            'message': f"Le produit {produit.name} a été ajouté au panier.",
            'produit': {
                'id': produit.id,
                'name': produit.name,
                'prix': produit.prix,
                'quantite': panier[str(produit_id)]['quantite'],
            },
            'total': total,
        })

    return JsonResponse({'success': False, 'message': "Requête invalide."}, status=400)


# Afficher le panier
@login_required
def panier(request):
    panier = request.session.get('panier', {})
    
    # Calcul du total avec les prix sous forme de float
    total = sum(item['prix'] * item['quantite'] for item in panier.values())

    # Récupération des produits dans le panier
    produits_panier = []
    for produit_id, details in panier.items():
        produit = get_object_or_404(Produit, id=produit_id)
        produits_panier.append({
            'produit': produit,
            'quantite': details['quantite'],
            'prix': details['prix'],  # Assurez-vous que prix est déjà un float
        })

    return render(request, 'pharma/panier.html', {'panier': produits_panier, 'total': total})

#Augmenter la quantiter

@login_required
def augmenter_quantite(request, produit_id):
    if request.method == 'POST':
        panier = request.session.get('panier', {})
        if str(produit_id) in panier:
            produit = get_object_or_404(Produit, id=produit_id)

            # Vérification du stock
            if produit.stock is None or produit.stock <= panier[str(produit_id)]['quantite']:
                return JsonResponse({'success': False, 'message': "Stock insuffisant."}, status=400)
            else:
                panier[str(produit_id)]['quantite'] += 1
                request.session['panier'] = panier
                return JsonResponse({
                    'success': True,
                    'quantite': panier[str(produit_id)]['quantite'],
                    'total': sum(
                        float(item['prix']) * item['quantite'] for item in panier.values()
                    )
                })
        return JsonResponse({'success': False, 'message': "Produit non trouvé dans le panier."}, status=404)

    return JsonResponse({'success': False, 'message': "Requête invalide."}, status=400)



#reduire_quantite
@login_required
def reduire_quantite(request, produit_id):
    if request.method == 'POST':
        panier = request.session.get('panier', {})
        if str(produit_id) in panier:
            if panier[str(produit_id)]['quantite'] > 1:
                panier[str(produit_id)]['quantite'] -= 1
            else:
                del panier[str(produit_id)]

            request.session['panier'] = panier
            return JsonResponse({
                'success': True,
                'quantite': panier.get(str(produit_id), {}).get('quantite', 0),
                'total': sum(
                    float(item['prix']) * item['quantite'] for item in panier.values()
                )
            })
        return JsonResponse({'success': False, 'message': "Produit non trouvé dans le panier."}, status=404)

    return JsonResponse({'success': False, 'message': "Requête invalide."}, status=400)


# Confirmer la commande

@login_required
def passer_au_paiement(request):
    panier = request.session.get('panier', {})

    # Vérifier que le panier n'est pas vide
    if not panier:
        messages.error(request, "Votre panier est vide. Ajoutez des produits avant de passer au paiement.")
        return redirect('panier')

    # Vérifier les stocks des produits dans le panier
    produits_indisponibles = []
    for produit_id, details in panier.items():
        produit = get_object_or_404(Produit, id=produit_id)
        if details['quantite'] > produit.stock:
            produits_indisponibles.append(produit.nom)

    # Si des produits sont indisponibles, afficher un message d'erreur
    if produits_indisponibles:
        messages.error(
            request,
            f"Les produits suivants ne sont pas disponibles en quantité suffisante : {', '.join(produits_indisponibles)}."
        )
        return redirect('panier')

    # Créer une commande pour l'utilisateur
    commande = Commande.objects.create(user=request.user, date_commande=now())

    # Ajouter les produits de la commande
    for produit_id, details in panier.items():
        produit = get_object_or_404(Produit, id=produit_id)
        CommandeProduit.objects.create(
            commande=commande,
            produit=produit,
            quantite=details['quantite'],
            prix_unitaire=details['prix']
        )

        # Réduire le stock du produit
        produit.stock -= details['quantite']
        produit.save()

    # Vider le panier après validation
    request.session['panier'] = {}

    # Rediriger vers une page de confirmation ou de paiement
    messages.success(request, "Votre commande a été enregistrée avec succès. Procédez au paiement.")
    return redirect('page_paiement')  # Remplacez 'page_paiement' par l'URL de votre page de paiement


from django.shortcuts import redirect

@login_required
def valider_paiement(request):
    if request.method == 'POST':
        # Exemple de création de commande après validation du paiement
        commande = Commande.objects.create(
            utilisateur=request.user,
            total=request.POST.get('total'),
            statut='payée'
        )

        # Ajouter les produits du panier à la commande
        panier = request.session.get('panier', {})
        for produit_id, details in panier.items():
            produit = Produit.objects.get(id=produit_id)
            CommandeProduit.objects.create(
                commande=commande,
                produit=produit,
                quantite=details['quantite']
            )
            # Mettre à jour le stock du produit
            produit.stock -= details['quantite']
            produit.save()

        # Vider le panier
        request.session['panier'] = {}

        # Rediriger vers la facture
        return redirect('facture', commande_id=commande.id)

    messages.error(request, "Une erreur est survenue.")
    return redirect('paiement')

#######

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Produit

def supprimer_produit(request, produit_id):
    if request.method == "POST":
        panier = request.session.get('panier', {})

        # Vérifier si le produit existe dans le panier
        if str(produit_id) in panier:
            # Supprimer le produit du panier
            del panier[str(produit_id)]

            # Mettre à jour le panier dans la session
            request.session['panier'] = panier

            # Calculer le total du panier
            total = sum(
                int(item['prix']) * item['quantite']
                for item in panier.values()
            )

            return JsonResponse({
                'success': True,
                'total': total,
                'message': 'Produit supprimé avec succès.'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Produit non trouvé dans le panier.'
            }, status=404)
    else:
        return JsonResponse({
            'success': False,
            'message': 'Méthode non autorisée.'
        }, status=405)

@login_required
def vider_panier(request):
    if request.method == 'POST':
        request.session['panier'] = {}
        return JsonResponse({'success': True, 'total': 0})
    else:
        return JsonResponse({'success': False, 'message': 'Requête invalide'}, status=400)
####""


# Afficher la facture avec QR code
@login_required
def facture(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    qr_data = f"Commande ID:{commande.id}, Client:{commande.client.username}, Montant:{commande.montant_total}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    
    # Convertir l'image en fichier pour l'afficher dans la facture
    buffer = BytesIO()
    img.save(buffer)
    qr_code_image = File(buffer, name=f"commande_{commande.id}_qr.png")
    
    return render(request, 'facture.html', {'commande': commande, 'qr_code': qr_code_image})

# Afficher les détails d'un produit
@login_required
def detail_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    # Vous pouvez aussi récupérer des informations comme les avis, les produits similaires, etc.
    # Par exemple, si vous avez un modèle d'avis :
    # avis = Avis.objects.filter(produit=produit)

    return render(request, 'pharma/detail_produit.html', {'produit': produit})
