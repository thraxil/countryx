from django.template import Context, loader
from genocideprevention.sim.models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

@login_required
def root(request):
   return render_to_response("sim/index.html",dict(user=request.user))

@login_required
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

@login_required
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
   