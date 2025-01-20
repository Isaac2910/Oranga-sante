from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('date_de_naissance', 'tel', 'img_assurance', 'num_assurance', 'adresse', 'historique_commandes', 'photo_de_profil')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('date_de_naissance', 'tel', 'img_assurance', 'num_assurance', 'adresse', 'historique_commandes', 'photo_de_profil')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
