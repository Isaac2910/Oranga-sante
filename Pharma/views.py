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
    articles = Article.objects.all() 
    return render(request, 'pharma/accueil.html', {'produits': produits, 'articles': articles})


#Ajouter au panier
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
#vider
@login_required
def vider_panier(request):
    if request.method == 'POST':
        request.session['panier'] = {}
        return JsonResponse({'success': True, 'total': 0})
    else:
        return JsonResponse({'success': False, 'message': 'Requête invalide'}, status=400)
####""



################

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, Commande, CommandeProduit
import qrcode
from io import BytesIO
from datetime import datetime
import json

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def paiement(request):
    panier = request.session.get('panier', {})
    if not panier:
        messages.error(request, "Votre panier est vide.")
        return redirect('pharma:accueil')  # Remplacez par le nom correct de l'URL

    try:
        # Calculer le total en vérifiant les clés
        total = sum(
            float(item.get('prix', 0)) * int(item.get('quantite', 0))
            for item in panier.values()
        )

        # Sauvegarder les données de paiement dans la session
        request.session['paiement_valide'] = {
            'total': total,
            'panier': panier,
        }

        # Afficher un message de succès
        messages.success(request, f"Paiement validé pour un total de {total:.2f} FCFA.")
        return redirect('pharma:generer_facture')  # Remplacez par le nom correct de l'URL

    except Exception as e:
        # Afficher un message d'erreur avec détails
        messages.error(request, f"Erreur lors du paiement : {str(e)}")
        return redirect('pharma:accueil')  # Remplacez par le nom correct de l'URL


##########facture
import base64

@login_required
def generer_facture(request):
    paiement_data = request.session.get('paiement_valide', None)
    if not paiement_data:
        messages.error(request, "Aucune transaction trouvée.")
        return redirect('pharma:panier')

    try:
        # Vérification que le total est un nombre valide
        total = float(paiement_data.get('total', 0))
        panier = paiement_data['panier']

        # Vérification s'il existe déjà une commande en cours pour l'utilisateur
        commande = Commande.objects.filter(client=request.user, statut='en_attente').first()

        if not commande:
            # Création de la commande
            commande = Commande.objects.create(client=request.user, total=total)

        produits = []
        for produit_id, details in panier.items():
            produit = get_object_or_404(Produit, id=produit_id)

            # Vérification de la quantité de stock avant mise à jour
            if produit.stock >= details['quantite']:  # Utilisation de 'quantite' ici
                # Ajouter le produit à la commande
                CommandeProduit.objects.create(
                    commande=commande,
                    produit=produit,
                    quantity=details['quantite'],  # Utilisation de 'quantite' ici aussi
                )

                produits.append({
                    'name': produit.name,
                    'prix': produit.prix,
                    'quantite': details['quantite'],  # 
                    'total': produit.prix * details['quantite'],
                })

                # Mise à jour du stock
                produit.stock -= details['quantite']  # Utilisation de 'quantite' ici aussi
                produit.save()
            else:
                # Stock insuffisant pour effectuer la commande
                messages.error(request, f"Le produit {produit.name} n'a pas suffisamment de stock.")
                return redirect('pharma:panier')

        # Génération du QR Code
        qr_data = {
            "commande_id": commande.id,
            "total": total,
            "client": request.user.username,
        }
        qr = qrcode.make(json.dumps(qr_data))
        qr_buffer = BytesIO()
        qr.save(qr_buffer)
        qr_buffer.seek(0)
        qr_code_url = f"data:image/png;base64,{base64.b64encode(qr_buffer.getvalue()).decode('utf-8')}"

        # Supprimer le panier de la session
        request.session['panier'] = {}

        # Rendu de la page facture
        return render(request, 'pharma/facture.html', {
            'commande': commande,
            'produits': produits,
            'qr_code_url': qr_code_url,
            'current_year': datetime.now().year,
        })

    except Exception as e:
        messages.error(request, f"Erreur lors de la génération de la facture : {e}")
        return redirect('pharma:panier')



@login_required
def historique_commandes(request):
    commandes = Commande.objects.filter(client=request.user).order_by('-date_commande')  # Récupère toutes les commandes de l'utilisateur
    return render(request, 'pharma/historique.html', {
        'commandes': commandes
    })
    
    
    
import qrcode
import base64
from io import BytesIO
from django.shortcuts import render, get_object_or_404

@login_required
def details_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id, client=request.user)
    produits = commande.commande_produits.all()

    # Calcul du total pour chaque produit
    for produit in produits:
        produit.total_prix = produit.quantity * produit.produit.prix

    # Inclure le nom du client dans les données du QR code
    client_name = commande.client.get_full_name()  # ou utilisez commande.client.username selon votre modèle
    qr_data = f"Commande ID: {commande.id} - Client: {client_name} - Total: {commande.total}€"

    # Générer le QR code avec les nouvelles données
    qr_img = qrcode.make(qr_data)

    # Convertir l'image en base64
    img_io = BytesIO()
    qr_img.save(img_io, 'PNG')
    img_io.seek(0)
    qr_code_base64 = base64.b64encode(img_io.read()).decode('utf-8')

    return render(request, 'pharma/details_commande.html', {
        'commande': commande,
        'produits': produits,
        'qr_code_base64': qr_code_base64,  # Passer l'image du QR code en base64 au template
    })

from django.shortcuts import render
from .models import Article







def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    related_articles = Article.objects.exclude(pk=pk)[:3]  # Les 3 articles similaires
    return render(request, "articles/article_detail.html", {
        "article": article,
        "related_articles": related_articles,
    })
