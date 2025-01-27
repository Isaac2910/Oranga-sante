from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    date_de_naissance = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True)
    tel = models.CharField(max_length=15, blank=True)
    img_assurance = models.ImageField(upload_to='assurance/', blank=True, null=True)
    num_assurance = models.CharField(max_length=50, blank=True)
    adresse = models.TextField(blank=True)

    photo_de_profil = models.ImageField(upload_to='photos_profil/', blank=True, null=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username



    groups = models.ManyToManyField(
        Group,
        related_name='customuser_groups',  # Utilisez un nom unique ici
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',  # Utilisez un nom unique ici
        blank=True,
    )