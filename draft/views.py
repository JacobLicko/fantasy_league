from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm


# Create your views here.
def home(request):
    login_form = AuthenticationForm(request, data=request.POST or None)
    signup_form = SignUpForm(request.POST or None)

    # Determine which button was clicked
    if request.method == 'POST':
        if 'login_submit' in request.POST and login_form.is_valid():
            user = login_form.get_user()
            auth_login(request,user)
            return redirect('dashboard')
        
        if 'signup_submit' in request.POST and signup_form.is_valid():
            user = signup_form.save()
            auth_login(request, user)
            return redirect('dashboard')
        
    return render(request, 'home.html', {'login_form': login_form, 'signup_form': signup_form,})

@login_required(login_url='landing')   # or 'login'
def dashboard(request):
    # blank homescreen after login/signup
    return render(request, 'dashboard.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user) # auto login after sign up
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
