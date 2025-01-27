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
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Votre email',
            'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1D82B6]'
        }),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Votre mot de passe',
            'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1D82B6]'
        }),
    )
    
    def get_redirect_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url  # Redirige vers l'URL 'next'
        return super().get_redirect_url() 

    
    
   

    


from django import forms
from .models import CustomUser

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['photo_de_profil', 'date_de_naissance', 'tel', 'adresse', 'num_assurance']
        widgets = {
            'photo_de_profil': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1D82B6]',
            }),
            'date_de_naissance': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1D82B6]',
            }),
            'tel': forms.TextInput(attrs={
                'placeholder': 'Entrez votre numéro de téléphone',
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1D82B6]',
            }),
            'adresse': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Entrez votre adresse complète',
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1D82B6]',
            }),
            'num_assurance': forms.TextInput(attrs={
                'placeholder': 'Entrez votre numéro d’assurance',
                'class': 'w-full px-4 py-2 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1D82B6]',
            }),
        }

    def clean_date_de_naissance(self):
        date_de_naissance = self.cleaned_data.get('date_de_naissance')
        if date_de_naissance:
            from datetime import date
            if date_de_naissance >= date.today():
                raise forms.ValidationError("La date de naissance doit être dans le passé.")
        return date_de_naissance

    def clean_tel(self):
        tel = self.cleaned_data.get('tel')
        if tel and not tel.isdigit():
            raise forms.ValidationError("Le numéro de téléphone ne doit contenir que des chiffres.")
        return tel
