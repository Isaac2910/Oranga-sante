
from django.shortcuts import render, redirect
from .forms import ProfileForm
from django.contrib.auth.decorators import login_required

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirige vers la page de profil
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'account/update_profile.html', {'form': form})

#####
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

@login_required
def modifier_profil(request):
    user = request.user  # L'utilisateur connecté
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profil')  # Redirection après modification réussie
    else:
        form = ProfileForm(instance=user)

    return render(request, 'modifier_profil.html', {'form': form})



@login_required
def profil(request):
    return render(request, 'profil.html', {'user': request.user})
