from django.template import Context, loader
from genocideprevention.sim.models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django import forms

@login_required
def root(request):
    # is the user a student or an administrator?
    qs = SectionAdministrator.objects.filter(user=request.user)
    if (len(qs) > 0):
        return faculty_index(request)
    else:
        return player_index(request)

    
###############################################################################
###############################################################################    

def faculty_index(request):
    sections = Section.objects.filter(sectionadministrator__user=request.user)
    return render_to_response("sim/faculty_index.html", dict(sections=sections, user=request.user))

def faculty_section(request, section_id):
    return render_to_response("sim/faculty_section.html", dict(user=request.user, section=Section.objects.get(id=section_id)))

def faculty_player(request, section_id, group_id, user_id, updated):
    section = Section.objects.get(id=section_id)
    group = SectionGroup.objects.get(id=group_id)
    player = group.sectiongroupplayer_set.get(user__id=user_id)
    current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
    choices = StateRoleChoice.objects.filter(state=current_state, role=player.role)
    player_turn = SectionGroupPlayerTurn.objects.filter(player=player, state=current_state)
        
    if (request.method == 'POST'):
        form = FeedbackForm(request.POST)
        if (form.is_valid()):
            # Process the data in form.cleaned_data
            player_turn.feedback = form.cleaned_data['feedback']
            player_turn.faculty = SectionAdministrator.objects.get(form.cleaned_data['faculty_id'])
            player_turn.save()
            
            redirect_url = 'sim/player/%s/%s/%s/%s' % (section_id, group_id, user_id, 1)
            return HttpResponseRedirect(redirect_url)
    else:
        form = FeedbackForm()
        
    return render_to_response("sim/faculty_player.html", 
        dict(user=request.user, section=section, group=group, player=player, choices=choices, player_turn=player_turn, form=form, updated=updated))
    
class FeedbackForm(forms.Form):
    feedback = forms.Textarea()
    faculty_id = forms.IntegerField()
    
###############################################################################
###############################################################################

def player_index(request):
    groups = SectionGroup.objects.filter(sectiongroupplayer__user=request.user)
    return render_to_response("sim/player_index.html", dict(user=request.user, groups=groups))

@login_required
def narrative(request, group_id, user_id):
    t = loader.get_template('sim/narrative.html')
    
    group = SectionGroup.objects.get(id=group_id)
    player = group.sectiongroupplayer_set.get(user__id=user_id)
    
    current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
    conditions = __current_conditions(current_state)
        
    c = Context({
       'group': group,
       'player': player,
       'state': current_state,
       'country_condition': current_state.statevariable_set.get(name='Country Condition').value,
       'conditions': conditions,
    })
    
    return HttpResponse(t.render(c))

@login_required
def decision(request, group_id, user_id):
    t = loader.get_template('sim/decision.html')
    
    group = SectionGroup.objects.get(id=group_id)
    player = group.sectiongroupplayer_set.get(user__id=user_id)
    
    current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
    conditions = __current_conditions(current_state)
    
    choices = StateRoleChoice.objects.filter(state=current_state, role=player.role)
    
    c = Context({
       'group': group,
       'player': player,
       'state': current_state,
       'conditions': conditions,
       'choices': choices
    })
    
    return HttpResponse(t.render(c))

def __current_conditions(state):
    conditions = []
    conditions.append(state.statevariable_set.get(name='Levels of Violence'))
    conditions.append(state.statevariable_set.get(name='Country\'s Economy'))
    conditions.append(state.statevariable_set.get(name='Prestige'))
    conditions.append(state.statevariable_set.get(name='Awareness'))
    conditions.append(state.statevariable_set.get(name='Political Discourse'))
    conditions.append(state.statevariable_set.get(name='Weapons Flow'))
    return conditions
   