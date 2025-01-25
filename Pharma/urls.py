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


    
]
