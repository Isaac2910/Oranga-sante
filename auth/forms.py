from allauth.account.forms import SignupForm, LoginForm
from django import forms
from .models import CustomUser

class CustomSignupForm(SignupForm):
    date_de_naissance = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="Date de naissance"
    )
    tel = forms.CharField(
        max_length=15,
        required=True,
        label="Téléphone"
    )
    img_assurance = forms.ImageField(
        required=False,
        label="Image de l'assurance"
    )
    num_assurance = forms.CharField(
        max_length=50,
        required=False,
        label="Numéro d'assurance"
    )
    adresse = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="Adresse"
    )
    photo_de_profil = forms.ImageField(
        required=False,
        label="Photo de profil"
    )

    def save(self, request):
        # Appel de la méthode parente pour enregistrer l'utilisateur
        user = super().save(request)
        # Ajouter les champs personnalisés au modèle utilisateur
        user.date_de_naissance = self.cleaned_data['date_de_naissance']
        user.tel = self.cleaned_data['tel']
        user.img_assurance = self.cleaned_data.get('img_assurance')
        user.num_assurance = self.cleaned_data.get('num_assurance')
        user.adresse = self.cleaned_data.get('adresse')
        if self.cleaned_data.get('photo_de_profil'):
            user.photo_de_profil = self.cleaned_data['photo_de_profil']
        user.save()
        return user

#Formulair  login
class CustomLoginForm(LoginForm):
    email = forms.EmailField(label="Email", max_length=254)
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnalisation des champs pour ajouter des classes CSS
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Votre Email'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Mot de passe'})



from django import forms
from .models import CustomUser  #

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['photo_de_profil', 'date_de_naissance', 'tel', 'adresse','num_assurance']  
        widgets = {
            'date_de_naissance': forms.DateInput(attrs={'type': 'date'}),
            'adresse': forms.Textarea(attrs={'rows': 3}),
        }
