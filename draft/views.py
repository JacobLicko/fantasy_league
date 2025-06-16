from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

def dashboard(request):
    # blank homescreen after login/signup
    return render(request, 'dashboard.html')