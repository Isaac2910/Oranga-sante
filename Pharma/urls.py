from django.urls import path
from . import views

urlpatterns = [
    path('ajouter_au_panier/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/', views.panier, name='panier'),
    path('payer/', views.payer, name='payer'),
    path('historique/', views.historique, name='historique'),
    path('produits/', views.produits, name='produits'),
]
