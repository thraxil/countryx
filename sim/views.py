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
    # is the user a player or an administrator?
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
def faculty_section_bygroup(request, section_id):
    return render_to_response("sim/faculty_section_bygroup.html", dict(user=request.user, section=Section.objects.get(id=section_id)))

def faculty_section_byplayer(request, section_id):
    return render_to_response("sim/faculty_section_byplayer.html", dict(user=request.user, section=Section.objects.get(id=section_id)))

@login_required
def faculty_group_detail(request, group_id):
    group = SectionGroup.objects.get(id=group_id)
    
    turns = []
    
    # for each completed state, list the players and their choices
    group_states = group.sectiongroupstate_set.order_by('-date_updated')
    for gs in group_states:
        # for each player, setup their actions
        player_turns = []
        
        players = group.sectiongroupplayer_set.all()
        for p in players:
            try:
                turn = SectionGroupPlayerTurn.objects.get(player=p, state=gs.state)
            except SectionGroupPlayerTurn.DoesNotExist:
                turn = None
                
            player_turns.append( { 'model': p, 'turn': turn, 'submit_status': p.status(gs.state) } )
            
        conditions = gs.state.statevariable_set.get(name='Country Condition').value
        turns.append( { 'group_state': gs, 'players': player_turns, 'country_condition': conditions } )
       
    ctx = Context({
       'user': request.user,
       'group': group,
       'turns': turns,
       'section': group.section,
    })
    
    template = loader.get_template('sim/faculty_group_detail.html')
    return HttpResponse(template.render(ctx))
    
@login_required
def faculty_player_detail(request, group_id, player_id, state_id, updated=False):
    group = SectionGroup.objects.get(id=group_id)
    player = SectionGroupPlayer.objects.get(id=player_id)
    state = State.objects.get(id=state_id)
    feedback = None
    
    try:
        turn = SectionGroupPlayerTurn.objects.get(player=player, state=state)
        feedback = turn.feedback
    except SectionGroupPlayerTurn.DoesNotExist:
        turn = None
        
    if (request.method == 'POST'):
        form = FeedbackForm(request.POST)
        if (form.is_valid()):
            # Process the data in form.cleaned_data
            turn.feedback = form.cleaned_data['feedback']
            turn.feedback_date = datetime.datetime.now()
            turn.faculty = SectionAdministrator.objects.get(section=group.section, user__id=form.cleaned_data['faculty_id'])
            turn.save()
                        
            redirect_url = '/sim/faculty/player/%s/%s/%s/1/' % (group_id, player_id, state_id)
            return HttpResponseRedirect(redirect_url)
    else:
        form = FeedbackForm(initial={'faculty_id': request.user.id, 'feedback': feedback })

    ctx = Context({
       'user': request.user,
       'group': group,
       'section': group.section,
       'player': player,
       'state': state,
       'turn': turn,
       'submit_status': player.status(state),
       'choices': StateRoleChoice.objects.filter(state=state, role=player.role),
       'country_condition': state.statevariable_set.get(name='Country Condition').value,
       'form': form,
       'updated': updated
    })
    
    template = loader.get_template('sim/faculty_player_detail.html')
    return HttpResponse(template.render(ctx))
  
class FeedbackForm(forms.Form):
    feedback = forms.CharField(widget=forms.Textarea)
    faculty_id = forms.IntegerField(widget=forms.HiddenInput)    
    
###############################################################################
###############################################################################

def __player_index(request):
    groups = SectionGroup.objects.filter(sectiongroupplayer__user=request.user)
    return render_to_response("sim/player_index.html", dict(user=request.user, groups=groups))

@login_required
def player_game(request, group_id, turn_id=0):
    group = SectionGroup.objects.get(id=group_id)
    
    if turn_id == 0:
        working_state = group.sectiongroupstate_set.latest().state
    else:
        working_state = group.sectiongroupstate_set.get(state__turn=turn_id).state
    
    tabs = []
    for i in range(1, 5):
        t = { 'id': i, 'activetab': (working_state.turn == i), 'viewable': False }
        try:
            group.sectiongroupstate_set.get(state__turn=i).state
            t['viewable'] = True
        except:
            pass
        tabs.append(t)
        
    # setup set of special attributes for current user
    your_player = { 'model': group.sectiongroupplayer_set.get(user__id=request.user.id), 'saved_turn': None, 'saved_choice': None }
    try:
        your_player['submit_status'] = your_player['model'].status(working_state)
        your_player['choices'] = StateRoleChoice.objects.filter(state=working_state, role=your_player['model'].role)
        your_player['saved_turn'] = SectionGroupPlayerTurn.objects.get(player=your_player['model'], state=working_state)
        your_player['saved_choice'] = StateRoleChoice.objects.get(state=working_state, role=your_player['model'].role, choice=your_player['saved_turn'].choice)
    except:
        pass
    
    # setup player list attributes
    players = []
    for p in group.sectiongroupplayer_set.all():
        if (p != your_player['model']):
            players.append({ 'model' : p, 'submit_status': p.status(working_state) })
                        
    c = Context({
       'user': request.user,
       'group': group,
       'state': working_state,
       'country_condition': working_state.statevariable_set.get(name='Country Condition').value,
       'conditions': __current_conditions(working_state),
       'tabs': tabs,
       'players': players,
       'you': your_player,
    })
    
    t = loader.get_template('sim/player_game.html')
    return HttpResponse(t.render(c))

@login_required
def player_choose(request):
    response = {}
    try:
        groupid = request.POST.get('groupid', None)
        choiceid = request.POST.get('choiceid', None)
        final = int(request.POST.get('final', False))
        reasoning = request.POST.get('reasoning', '')
        
        group = SectionGroup.objects.get(id=groupid)
        player = group.sectiongroupplayer_set.get(user__id=request.user.id)
        current_state = group.sectiongroupstate_set.latest().state
            
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
   