from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .models import Photo
from .forms import PhotoForm, RegisterForm


def gallery_view(request):
    photos = Photo.objects.all().order_by('-uploaded_at')
    return render(
        request,
        'snapx/gallery.html',
        {
            'photos': photos,
            'is_new_visitor': not request.user.is_authenticated,
        },
    )


def logout_view(request):
    logout(request)
    return redirect('gallery')


@login_required(login_url='login')
def add_photo_view(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.author = request.user
            photo.save()
            return redirect('gallery')
    else:
        form = PhotoForm()
    return render(request, 'snapx/add_photo.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('gallery')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('gallery')

    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})
