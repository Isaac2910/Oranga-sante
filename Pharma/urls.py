from django.urls import path
from . import views

app_name = 'pharma'

urlpatterns = [
    path('', views.produit_list, name='produit_list'),
    
    path('ajouter-au-panier/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/', views.panier, name='panier'),
    path('augmenter-quantite/<int:produit_id>/', views.augmenter_quantite, name='augmenter_quantite'),
    path('reduire-quantite/<int:produit_id>/', views.reduire_quantite, name='reduire_quantite'),
    path('supprimer-produit/<int:produit_id>/', views.supprimer_produit, name='supprimer_produit'),
    path('vider-panier/', views.vider_panier, name='vider_panier'),
    
    path('paiement/', views.paiement, name='paiement'),
    path('facture/', views.generer_facture, name='generer_facture'),
    
        # URL pour afficher l'historique des commandes
    path('historique/', views.historique_commandes, name='historique'),

    # URL pour afficher les détails d'une commande spécifique
    path('commande/<int:commande_id>/', views.details_commande, name='details_commande'),
  


    
]
