from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, JoinLeagueForm, CreateLeagueForm
from .models import League


# Create your views here.
def landing(request):
    login_form = AuthenticationForm(request, data=request.POST or None)
    signup_form = SignUpForm(request.POST or None)

    # Determine which button was clicked
    if request.method == 'POST':
        if 'login_submit' in request.POST and login_form.is_valid():
            user = login_form.get_user()
            auth_login(request,user)
            return redirect('home')
        
        if 'signup_submit' in request.POST and signup_form.is_valid():
            user = signup_form.save()
            auth_login(request, user)
            return redirect('home')
        
    return render(request, 'landing.html', {'login_form': login_form, 'signup_form': signup_form,})

@login_required(login_url='landing')   # or 'login'
def home(request):
    leagues = request.user.leagues.all()
    join_form = JoinLeagueForm(request.POST or None)
    join_active = False
    create_form = CreateLeagueForm(request.POST or None)
    create_active = False

    # JOIN LEAGUE logic
    if request.method == 'POST' and 'join_submit' in request.POST:
        if join_form.is_valid():
            league = League.objects.get(code=join_form.cleaned_data['code'])
            league.members.add(request.user)
            join_success = True
            return redirect('league_detail', code=league.code)
        else:
            join_active = True

    # CREATE LEAGUE logic
    if 'create_submit' in request.POST:
        if create_form.is_valid():
            league = create_form.save(commit=False)
            league.creator = request.user
            league.save()
            league.members.add(request.user)
            return redirect('league_detail', code=league.code)
        else:
            create_active = True

    return render(request, 'home.html', {
        'leagues' : leagues,
        'join_form' : join_form,
        'join_active' : join_active,
        'create_form' : create_form,
        'create_active' : create_active,
    })

@login_required(login_url='landing')
def create_league(request):
    form = CreateLeagueForm(request.POST or None)
    if request.method == 'POST' and 'create_submit' in request.POST:
        if form.is_valid():
            cd = form.cleaned_data
            league = League.objects.create(
                name = cd['name'],
                max_players = cd['max_players'],
                draft_type = cd['draft_type'],
                region = cd['region'],
                draft_date = cd['draft_date'],
                draft_time = cd['draft_time'],
                creator = request.user,
            )
            league.members.add(request.user)
            return redirect('home')
    return render(request, 'create_league.html', {'form': form})

@login_required(login_url='landing')
def league_detail(request,code):
    #only let members see their league
    league = get_object_or_404(League, code=code, members=request.user)

    # Build a fixed length slots list
    members = list(league.members.all())
    empty_slots = league.max_players - len(members)
    slots = members + [None] * empty_slots

    # Only Creator may save/delete
    if request.method == 'POST' and league.creator == request.user:
        # Save edits
        if 'save_changes' in request.POST:
            league.name = request.POST.get('name')
            league.draft_type = request.POST.get('draft_type')
            league.draft_date = request.POST.get('draft_date')
            league.draft_time = request.POST.get('draft_time')
            league.save()
            return redirect('league_detail', code=league.code)
        
        # Confirm delete
        if 'delete_confirm' in request.POST:
            league.delete()
            return redirect('home')

    return render(request, 'league_detail.html', {'league': league, 'slots':slots})