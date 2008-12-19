from django.template import Context, loader
from genocideprevention.sim.models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django import forms
import datetime
import simplejson

@login_required
def root(request):
    # is the user a student or an administrator?
    qs = SectionAdministrator.objects.filter(user=request.user)
    if (len(qs) > 0):
        return __faculty_index(request)
    else:
        return __player_index(request)
    
###############################################################################
###############################################################################    

def __faculty_index(request):
    sections = Section.objects.filter(sectionadministrator__user=request.user)
    return render_to_response("sim/faculty_index.html", dict(sections=sections, user=request.user, port=request.META['SERVER_PORT'], hostname=request.META['SERVER_NAME']))

@login_required
def faculty_section(request, section_id):
    return render_to_response("sim/faculty_section.html", dict(user=request.user, section=Section.objects.get(id=section_id)))

@login_required
def faculty_player(request, section_id, group_id, player_id, updated=False):
    section = Section.objects.get(id=section_id)
    group = SectionGroup.objects.get(id=group_id)
    player = group.sectiongroupplayer_set.get(user__id=player_id)
    current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
    choices = StateRoleChoice.objects.filter(state=current_state, role=player.role)
    player_turn = None
        
    if (request.method == 'POST'):
        form = FeedbackForm(request.POST)
        if (form.is_valid()):
            # Process the data in form.cleaned_data
            player_turn = SectionGroupPlayerTurn.objects.filter(player=player, state=current_state)
            player_turn.feedback = form.cleaned_data['feedback']
            player_turn.faculty = SectionAdministrator.objects.get(section=section, user__id=form.cleaned_data['faculty_id'])
            player_turn.save()
            
            redirect_url = 'sim/faculty/player/%s/%s/%s/%s' % (section_id, group_id, player_id, 1)
            return HttpResponseRedirect(redirect_url)
    else:
        form = FeedbackForm(initial={'faculty_id': request.user.id})
        
    return render_to_response("sim/faculty_player.html", 
        dict(user=request.user, section=section, group=group, player=player, choices=choices, player_turn=player_turn, form=form, updated=updated))
    
class FeedbackForm(forms.Form):
    feedback = forms.CharField(widget=forms.Textarea)
    faculty_id = forms.IntegerField(widget=forms.HiddenInput)    
    
###############################################################################
###############################################################################

def __player_index(request):
    groups = SectionGroup.objects.filter(sectiongroupplayer__user=request.user)
    return render_to_response("sim/player_index.html", dict(user=request.user, groups=groups))

@login_required
def game(request, group_id):
    group = SectionGroup.objects.get(id=group_id)
    current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
    player = group.sectiongroupplayer_set.get(user__id=request.user.id)
    
    # Player's current submit state for this turn
    # 0 -- No action taken for this turn
    # 1 -- Draft Submitted
    # 2 -- Final Submission
    try:
        saved_turn = SectionGroupPlayerTurn.objects.get(player=player, state=current_state)
        saved_choice = StateRoleChoice.objects.get(state=current_state, role=player.role, choice=saved_turn.choice)
        if (saved_turn.submit_date == None):
            submit_state = 1
        else:    
            submit_state = 2
    except:
        submit_state = 0
        saved_turn = None
        saved_choice = None
        
    c = Context({
       'user': request.user,
       'group': group,
       'you': player,
       'state': current_state,
       'country_condition': current_state.statevariable_set.get(name='Country Condition').value,
       'conditions': __current_conditions(current_state),
       'choices': StateRoleChoice.objects.filter(state=current_state, role=player.role),
       'submit_state': submit_state,
       'saved_turn': saved_turn,
       'saved_choice': saved_choice 
    })
    
    t = loader.get_template('sim/player_game.html')
    return HttpResponse(t.render(c))

@login_required
def choose(request):
    response = {}
    try:
        groupid = request.POST.get('groupid', None)
        choiceid = request.POST.get('choiceid', None)
        final = int(request.POST.get('final', False))
        reasoning = request.POST.get('reasoning', '')
        
        group = SectionGroup.objects.get(id=groupid)
        player = group.sectiongroupplayer_set.get(user__id=request.user.id)
        current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
            
        # create or update the player's choice
        try:
            turn = SectionGroupPlayerTurn.objects.get(player=player, state=current_state)
        except:
            turn = SectionGroupPlayerTurn.objects.create(player=player, state=current_state)
        
        if turn.submit_date != None:
            # player has already submitted data
            response['result'] = 0
            response['message'] = 'Player has already submitted a final choice'
        else:
            turn.choice = choiceid
            turn.reasoning = reasoning
            if final:
               turn.submit_date = datetime.datetime.now()
            turn.save() 
             
            if (final):
                response['result'] = 2
                response['message'] = "Your choice and reasoning have been submitted"
            else:
                response['result'] = 1
                response['message'] = "Draft has been saved"
    except:
        response['result'] = 0
        response['message'] = "An unexpected error occurred. Please try again"
        
    return HttpResponse(simplejson.dumps(response), 'application/json')
                
def __current_conditions(state):
    conditions = []
    conditions.append(state.statevariable_set.get(name='Levels of Violence'))
    conditions.append(state.statevariable_set.get(name='Country\'s Economy'))
    conditions.append(state.statevariable_set.get(name='Prestige'))
    conditions.append(state.statevariable_set.get(name='Awareness'))
    conditions.append(state.statevariable_set.get(name='Political Discourse'))
    conditions.append(state.statevariable_set.get(name='Weapons Flow'))
    return conditions

#
#@login_required
#def narrative(request, group_id, user_id):
#    t = loader.get_template('sim/player_narrative.html')
#    
#    group = SectionGroup.objects.get(id=group_id)
#    player = group.sectiongroupplayer_set.get(user__id=user_id)
#    
#    current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
#    conditions = __current_conditions(current_state)
#    choices = StateRoleChoice.objects.filter(state=current_state, role=player.role)
#        
#    c = Context({
#       'group': group,
#       'player': player,
#       'state': current_state,
#       'country_condition': current_state.statevariable_set.get(name='Country Condition').value,
#       'conditions': conditions,
#       'choices': choices,
#    })
#    
#    return HttpResponse(t.render(c))
#
#@login_required
#def decision(request, group_id, user_id):
#    group = SectionGroup.objects.get(id=group_id)
#    player = group.sectiongroupplayer_set.get(user__id=user_id)
#   
#    current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
#    conditions = __current_conditions(current_state)
#   
#    choices = StateRoleChoice.objects.filter(state=current_state, role=player.role)
#        
#    if (request.method == 'POST'):
#        form = DecisionForm(request.POST)
#        if (form.is_valid()):
#            # Process the data in form.cleaned_data
#            choice = form.cleaned_data['choice']
#            reasoning = form.cleaned_data['reasoning']
#           
#            player_turn = SectionGroupPlayerTurn.objects.create(player=player, state=current_state, choice=choice, date_submitted=datetime.now(), reasoning=reasoning) 
#            
#            redirect_url = 'sim/'
#            return HttpResponseRedirect(redirect_url)
#    else:
#        form = DecisionForm(choices)
#        #form = DecisionForm()
#        
#    return render_to_response("sim/player_decision.html", 
#        dict(user=request.user, group=group, player=player, form=form, conditions=conditions, state=current_state))
#
#class DecisionForm(forms.Form):
#    choice_list = None
#    choice = forms.ModelChoiceField(label="Pick something", queryset=choice_list) 
#    reasoning = forms.CharField(widget=forms.Textarea)
#    
#    def __init__(self, choice_list, *args, **kw):
#        forms.Form.__init__(self, *args, **kw) 
#        self.choice.queryset = choice_list

#def status(request):
#    response = {}
#    
#    try:
#        groupid = request.POST.get('groupid', None)
#        player = group.sectiongroupplayer_set.get(user__id=request.user_id)
#        current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
#        
#        response['players'] = []
#        
#        # Status
#        # -- No action taken for this turn
#        # -- Draft Submitted
#        # -- Final Submission
#    
#        for player in group.sectiongroupplayer_set.all():
#            player = {}
#            player['role'] = player.role.name
#            
#            # get the turn
#            try:
#                turn = SectionGroupPlayerTurn.objects.get(player=player, state=current_state)
#                if (turn.submit_date == None):
#                    player['status'] = 1
#                else:
#                    player['status'] = 2
#            except:
#                player['status'] = 0
#            
#            players.push(player)
#            
#        response['result'] = 1
#        response['message'] = "Player statuses retrieved succesfully"
#    except:
#        response['result'] = 0
#        response['message'] = "An unexpected error occurred. Please try again"
#     
#    return HttpResponse(simplejson.dumps(response), 'application/json')
   