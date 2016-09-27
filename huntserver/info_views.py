from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import random

from utils import team_from_user_hunt
from .models import *
from .forms import *

def index(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    return render(request, "index.html", {'curr_hunt': curr_hunt})

def current_hunt_info(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    return render(request, "hunt_info.html", {'curr_hunt': curr_hunt})

def previous_hunts(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    if(curr_hunt.is_public):
        old_hunts = Hunt.objects.all().order_by('hunt_number')
    else:
        old_hunts = Hunt.objects.all().exclude(hunt_number=settings.CURRENT_HUNT_NUM).order_by('hunt_number')

    return render(request, "previous_hunts.html", {'hunts': old_hunts})

def registration(request):
    curr_hunt = Hunt.objects.get(hunt_number=settings.CURRENT_HUNT_NUM)
    team = team_from_user_hunt(request.user, curr_hunt)
    if(request.method == 'POST' and "form_type" in request.POST):
        if(request.POST["form_type"] == "new_team"):
            if(curr_hunt.team_set.filter(team_name__iexact=request.POST.get("team_name")).exists()):
                messages.error(request, 'This team already exists, please choose a new name')
                return HttpResponseRedirect('/registration/')
            if(request.POST.get("team_name") != ""):
                join_code = ''.join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(5))
                team = Team.objects.create(team_name=request.POST.get("team_name"), hunt=curr_hunt, 
                                           location=request.POST.get("need_room"), join_code=join_code)
                request.user.person.teams.add(team)
                redirect('huntserver:registration')
        elif(request.POST["form_type"] == "join_team"):
            team = curr_hunt.team_set.get(team_name=request.POST.get("team_name"))
            if(len(team.person_set.all()) >= team.hunt.team_size):
                messages.error(request, 'Team is full, please remove a person and try again.')
                return HttpResponseRedirect('/registration/')
            if(team.join_code.lower() != request.POST.get("join_code").lower()):
                messages.error(request, 'Team Join Code is incorrect, please try again')
                redirect('/registration/')
            request.user.person.teams.add(team)
            redirect('huntserver:registration')
    if("leave_team" in request.GET and request.GET["leave_team"] == "1"):
        request.user.person.teams.remove(team)
        team = None
    if(team != None):
        return render(request, "registration.html", {'registered_team': team})
    else:
        teams = Team.objects.filter(hunt=curr_hunt).all()
        return render(request, "registration.html", {'teams': teams})

