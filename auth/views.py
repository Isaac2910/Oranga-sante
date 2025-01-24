
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

