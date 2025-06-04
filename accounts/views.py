from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm
from core.models import MasterProfile, ClientProfile, User
from django.contrib import messages

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Создаем профиль в зависимости от роли
            if user.role == 'master':
                MasterProfile.objects.create(user=user)
            elif user.role == 'client':
                ClientProfile.objects.create(user=user)
            messages.success(request, 'Регистрация прошла успешно. Теперь войдите в систему.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    user = request.user
    if user.role == 'master':
        profile = getattr(user, 'master_profile', None)
    elif user.role == 'client':
        profile = getattr(user, 'client_profile', None)
    else:
        profile = None
    return render(request, 'accounts/profile.html', {'profile': profile, 'user': user})
