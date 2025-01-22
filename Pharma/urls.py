from django.urls import path
from . import views




urlpatterns = [
    # Produits
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produits/<int:produit_id>/', views.detail_produit, name='detail_produit'),

    # Panier
    path('panier/', views.afficher_panier, name='afficher_panier'),
    path('panier/ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/vider/', views.vider_panier, name='vider_panier'),

    # Commandes
    path('commandes/', views.creer_commande, name='creer_commande'),
    path('commandes/<int:commande_id>/', views.detail_commande, name='detail_commande'),
   
]
