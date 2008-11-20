from django.template import Context, loader
from genocideprevention.sim.models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.sites.models import Site
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, login, logout

class LoginForm(forms.Form):
    username = forms.CharField(label=_("Username"), max_length=30)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

def root(request):
    if (not request.user.is_authenticated()):
        return HttpResponseRedirect('/sim/login/')
    else:
        return index(request)

def index(request):
    t = loader.get_template('sim/index.html')
    
    c = Context({
       'user': request.user,
    })
    
    return HttpResponse(t.render(c))

def narrative(request, group_id, player_id):
    t = loader.get_template('sim/narrative.html')
    
    group = Group.objects.get(id=group_id)
    player = group.player_set.get(id=player_id)
    
    conditions = __current_conditions(group)
    
    c = Context({
       'group': group,
       'player': player,
       'country_condition': group.current_state.statevariable_set.get(name='Country Condition').value,
       'conditions': conditions,
    })
    
    return HttpResponse(t.render(c))

def decision(request, group_id, player_id):
    t = loader.get_template('sim/decision.html')
    
    group = Group.objects.get(id=group_id)
    player = group.player_set.get(id=player_id)
    
    conditions = __current_conditions(group)
    
    choices = StateRoleChoice.objects.filter(state=group.current_state, role=player.role)
    
    c = Context({
       'group': group,
       'player': player,
       'conditions': conditions,
       'choices': choices
    })
    
    return HttpResponse(t.render(c))

def __current_conditions(group):
    conditions = []
    conditions.append(group.current_state.statevariable_set.get(name='Levels of Violence'))
    conditions.append(group.current_state.statevariable_set.get(name='Country\'s Economy'))
    conditions.append(group.current_state.statevariable_set.get(name='Prestige'))
    conditions.append(group.current_state.statevariable_set.get(name='Awareness'))
    conditions.append(group.current_state.statevariable_set.get(name='Political Discourse'))
    conditions.append(group.current_state.statevariable_set.get(name='Weapons Flow'))
    return conditions

   