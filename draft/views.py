from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import SignUpForm, JoinLeagueForm, CreateLeagueForm
from .models import League, DraftSession
from django.http import JsonResponse, Http404
from django.utils import timezone
from datetime import datetime, timedelta


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

@login_required
def start_draft_session(request, code):
    league = get_object_or_404(League, code=code, members=request.user)
    # First combine separate date & time into one datetime
    naive_dt = datetime.combine(league.draft_date, league.draft_time)
    draft_dt = timezone.make_aware(naive_dt, timezone.get_current_timezone())
    # Only allow clicking once the button is enabled 
    if timezone.now() < draft_dt:
        return JsonResponse({'error': 'Too early'}, status=400)
    
    # 2) Sticky "started" check
    try:
        session = league.draft_session
        if session.started and not session.is_expired():
            return JsonResponse({
                'expires_at' : session.expires_at.isoformat(),
                'ready' : [u.username for u in session.ready.all()],
                'total' : league.members.count()
            })
    except DraftSession.DoesNotExist:
        pass


    # Get existing session if any
    try:
        session = league.draft_session
        # If it is expired, reset times and clear flags
        if session.is_expired():
            session.start_time = timezone.now()
            session.expires_at = timezone.now() + timedelta(minutes=2)
            session.ready.clear()
            session.started = False
            session.save()
    except DraftSession.DoesNotExist:
        # First click ever, create new session
        session = DraftSession.objects.create(
            league=league,
            start_time = timezone.now(),
            expires_at = timezone.now() + timedelta(minutes=2),
            started = False,
        )
    
    # Now just add this user, do not clear other users
    session.ready.add(request.user)

    return JsonResponse({
        'expires_at' : session.expires_at.isoformat(),
        'ready' : [u.username for u in session.ready.all()],
        'total' : league.members.count(),
    })

@login_required
def draft_status(request, code):
    league = get_object_or_404(League, code=code, members=request.user)
    try:
        session = league.draft_session
    except DraftSession.DoesNotExist:
        return JsonResponse({'active' : False})
    
    # if expired and did NOT start, reset
    if session.is_expired() and not session.started:
        # if expired, reset it
        session.delete()
        return JsonResponse({'active' : False})
    
    ready_usernames = [u.username for u in session.ready.all()]
    all_ready = len(ready_usernames) == league.members.count()

    # If everyone is ready and the session has not started, start it
    if all_ready and not session.started:
        session.started = True
        session.save()

    return JsonResponse({
        'active' : True,
        'expires_at' : session.expires_at.isoformat(),
        'ready' : ready_usernames,
        'all_ready' : all_ready,
    })

@login_required
def draft_view(request, code):
    # 1) Must be a member of the league
    league = get_object_or_404(League, code=code, members=request.user)

    # 2) Must have an active DraftSession
    try:
        session = league.draft_session
    except DraftSession.DoesNotExist:
        # Draft has not started yet
        raise PermissionDenied("Draft has not been started.")
    
    # 3) Session must still be running
    if session.is_expired() and not session.started:
        # 2 minute window expired
        raise PermissionDenied("Draft Session has expired, please start again.")
    
    # 4) All members must be “ready”
    total_members = league.members.count()
    ready_count = session.ready.count()
    if not session.started:
        if ready_count < total_members:
            # Not everyone is ready
            raise PermissionDenied("Waiting for all players to ready up.")
    
    # If we get here, user is logged in, in the league, draft is active, everyone is ready
    return render(request, 'draft_view.html', {'league' : league})

# Delete this method later, for testing purposes
@login_required(login_url='landing')
def reset_draft_session(request, code):
    # Only league members (or you could restrict further to creator)
    league = get_object_or_404(League, code=code, members=request.user)

    try:
        session = league.draft_session
    except DraftSession.DoesNotExist:
        # Nothing to reset—just go back
        return redirect('draft_view', code=league.code)

    # Reset the “started” flag and clear ready users
    session.started = False
    session.ready.clear()
    session.save()

    return redirect('draft_view', code=league.code)