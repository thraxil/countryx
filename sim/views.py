from django.template import Context, loader
from countryx.sim.models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.template import Context, loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django import forms
from django.forms.util import ErrorList 
from django.contrib.admin.widgets import AdminSplitDateTime
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
    section = Section.objects.get(id=section_id)
    all_players = SectionGroupPlayer.objects.filter(group__section=section)
    
    ctx = Context({
       'user': request.user,
       'section': section,
       'players': all_players,
    })
    
    template = loader.get_template('sim/faculty_section_byplayer.html')
    return HttpResponse(template.render(ctx))

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
                turn = SectionGroupPlayerTurn.objects.get(player=p, turn=gs.state.turn)
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
def faculty_player_detail_byturn(request, group_id, player_id, state_id, updated=False):
    group = SectionGroup.objects.get(id=group_id)
    player = SectionGroupPlayer.objects.get(id=player_id, group=group)
    state = State.objects.get(id=state_id)
    feedback = None
    
    try:
        turn = SectionGroupPlayerTurn.objects.get(player=player, turn=state.turn)
        feedback = turn.feedback
    except SectionGroupPlayerTurn.DoesNotExist:
        pass # should never happen

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
       'form': FeedbackForm(initial={'faculty_id': request.user.id, 'feedback': feedback, 'turn_id': state.turn }),
       'updated': updated
    })
    
    template = loader.get_template('sim/faculty_player_detail_byturn.html')
    return HttpResponse(template.render(ctx))

@login_required
def faculty_player_detail(request, player_id):
    player = SectionGroupPlayer.objects.get(id=player_id)
    group = player.group
    
    player_turns = []
    turns = SectionGroupPlayerTurn.objects.filter(player=player).order_by("-turn")
    
    for t in turns:
        turn_state = group.sectiongroupstate_set.get(state__turn=t.turn).state
        player_turn = {'turn': t.turn, 
                       'submit_status': player.status(turn_state),
                       'choice': t.choice,
                       'choices': StateRoleChoice.objects.filter(state=turn_state, role=player.role),
                       'country_condition': turn_state.statevariable_set.get(name='Country Condition').value,
                       'submit_date': t.submit_date,
                       'reasoning': t.reasoning,
                       'state': turn_state,
                       'automatic_update': t.automatic_update,
                       'form': FeedbackForm(initial={'faculty_id': request.user.id, 'feedback': t.feedback, 'turn_id': t.turn}),
                       }
 
        player_turns.append(player_turn)
                
    ctx = Context({
       'user': request.user,
       'player': player,
       'group': group,
       'section': group.section,
       'player_turns': player_turns
    })

    template = loader.get_template('sim/faculty_player_detail.html')
    return HttpResponse(template.render(ctx))

def faculty_feedback_submit(request):
    response = {}
    try:
        player_id = request.POST.get('player_id', None)
        faculty_id = int(request.POST.get('faculty_id', None))
        turn_id = int(request.POST.get('turn_id', None))
        feedback = request.POST.get('feedback', '')
        
        player = SectionGroupPlayer.objects.get(id=player_id)
        group = player.group
        
        # Retrieve the associated player turn to update
        turn = SectionGroupPlayerTurn.objects.get(player=player, turn=turn_id)
        
        turn.feedback = feedback
        turn.feedback_date = datetime.datetime.now()
        turn.faculty = SectionAdministrator.objects.get(section=group.section, user__id=faculty_id)
        turn.save()
             
        response['result'] = 1
        response['turn_id'] = turn_id
        response['message'] = "Your feedback has been saved."
    except:
        response['result'] = 0
        response['turn_id'] = turn_id
        response['message'] = "An unexpected error occurred. Please try again"
        
    return HttpResponse(simplejson.dumps(response), 'application/json')
 
class FeedbackForm(forms.Form):
    feedback = forms.CharField(widget=forms.Textarea)
    faculty_id = forms.IntegerField(widget=forms.HiddenInput)
    turn_id = forms.IntegerField(widget=forms.HiddenInput)    
    
@login_required
def faculty_section_manage(request, section_id, updated=False):
    section=Section.objects.get(id=section_id)
        
    if (request.method == 'POST'):
        form = TurnManagementForm(request.POST)
        if (form.is_valid()):
            # Process the data in form.cleaned_data
            try:
               tm = SectionTurnDates.objects.get(section=section)
            except:
               tm = SectionTurnDates.objects.create(section=section, turn1=datetime.datetime.now())
               
            section.name = form.cleaned_data['section_name']
            section.term = form.cleaned_data['section_term']
            section.year = form.cleaned_data['section_year']
            section.save()
            
            tm.turn1 = form.cleaned_data['turn1']
            tm.turn2 = form.cleaned_data['turn2']
            tm.turn3 = form.cleaned_data['turn3']
            
            tm.save()
                        
            redirect_url = '/sim/faculty/manage/%s/' % (section_id)
            return HttpResponseRedirect(redirect_url)
    else:
        initial = {}
        initial['section_name'] = section.name
        initial['section_term'] = section.term
        initial['section_year'] = section.year
            
        try:
            tm = SectionTurnDates.objects.get(section=section)
            initial['turn1'] = tm.turn1
            initial['turn2'] = tm.turn2
            initial['turn3'] = tm.turn3
        except:
            initial['turn1'] = datetime.datetime.now()
        
        form = TurnManagementForm(initial=initial)

    ctx = Context({
       'user': request.user,
       'section': section,
       'form': form,
       'updated': updated
    })
    
    template = loader.get_template('sim/faculty_section_manage.html')
    return HttpResponse(template.render(ctx))
  
EMPTY_VALUES = (None, '')

class DateTimeFieldEx(forms.DateTimeField):
    def clean(self, value):
        if not self.required and value[0] in EMPTY_VALUES and value[1] in EMPTY_VALUES:
            return None
        return super(DateTimeFieldEx, self).clean(value)
    
class TurnManagementForm(forms.Form):
    section_name = forms.CharField()
    section_term = forms.CharField()
    section_year = forms.CharField()
    
    turn1 = DateTimeFieldEx(widget=AdminSplitDateTime, required=True, label="Turn 1 Close Date")
    turn2 = DateTimeFieldEx(widget=AdminSplitDateTime, required=False, label="Turn 2 Close Date")
    turn3 = DateTimeFieldEx(widget=AdminSplitDateTime, required=False, label="Turn 3 Close Date")
    
    def __compare(self, cleaned_data, fieldOne, fieldTwo, labelOne, labelTwo):
        if (fieldTwo in cleaned_data and not cleaned_data[fieldTwo] in EMPTY_VALUES): 
            if (fieldOne in cleaned_data and not cleaned_data[fieldOne] in EMPTY_VALUES and cmp(cleaned_data[fieldOne], cleaned_data[fieldTwo]) > -1):
                msg = "%s close date must be after %s close date" % (labelTwo, labelOne)
                self._errors[fieldTwo] = ErrorList([msg])
                del cleaned_data[fieldTwo]
                
    def clean(self):
        cleaned_data = self.cleaned_data
        
        self.__compare(cleaned_data, "turn1", "turn2", "Turn 1", "Turn 2")
        
        self.__compare(cleaned_data, "turn1", "turn3", "Turn 1", "Turn 3")
        self.__compare(cleaned_data, "turn2", "turn3", "Turn 2", "Turn 3")
        
        return cleaned_data
    
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

        if i < 4:
            t['name'] = 'Phase %s' % i
        else:
            t['name'] = "Results" 
        
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
        your_player['saved_turn'] = SectionGroupPlayerTurn.objects.get(player=your_player['model'], turn=working_state.turn)
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

#actually needs to be faculty only
@login_required 
def allquestions(request):
    response = {}
    for x in StateRoleChoice.objects.all():
        response.setdefault(x.state.id,{}).setdefault(x.role.name,{}).setdefault(x.choice,x.desc)
    return HttpResponse(simplejson.dumps(response), 'application/json')

#actually needs to be faculty only
@login_required 
def allvariables(request):
    response = {}
    for x in StateVariable.objects.all():
        response.setdefault(x.state.id,{}).setdefault(x.name,x.value)
    return HttpResponse(simplejson.dumps(response), 'application/json')

@login_required 
def allpaths(request):
    t = loader.get_template('sim/allpaths.html')
    turns = []
    roles = ('president','regional','envoy','opposition')
    #NOTE: we currently assume 4 turns indexed at 1
    for turn in range(1,5):
        states = State.objects.filter(turn=turn).order_by("state_no")
        turn = {'states':[]}
        for s in states:
            turn['states'].append({'id':s.id,
                                   'state_no':s.state_no,
                                   'name':s.name,
                                   'full_from':s.full_from(roles),
                                   'full_to':s.full_to(roles),
                                   'color':s.get_color(),
                                   })
        turns.append(turn)
            
    c = Context({'turns':turns,'roles':roles})
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
        player = group.sectiongroupplayer_set.get(user__id=request.user.id, group=group)
        current_state = group.sectiongroupstate_set.latest().state
            
        # create or update the player's choice
        try:
            turn = SectionGroupPlayerTurn.objects.get(player=player, turn=current_state.turn)
        except:
            turn = SectionGroupPlayerTurn.objects.create(player=player, turn=current_state.turn)
        
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
    details = {'Violence Level':{'least': 'non-violent',
                                 'most': 'genocide',
                                 'good_inverse':True},
               'Economy':{'least': 'stable',
                          'most': 'depression'  },
               'Prestige':{'least': 'respected world player',
                           'most': 'globally isolated'  },
               'Awareness':{'least': 'regular media coverage',
                            'most': 'zero media coverage'  },
               'Political Discourse':{'least': 'free and open system',
                                      'most': 'state control of information'},
               'Weapons Flow':{'least': 'minimal/no weapons smuggling',
                               'most': 'uncontrolled weapons smuggling',
                               'good_inverse':True},
               }
    for k,v in details.items():
        var = state.statevariable_set.get(name=k)
        var_dict = details[k]
        var_dict['name'] =var.name
        if var_dict.get('good_inverse',False):
            var_dict['value'] =11-int(var.value)
        else:
            var_dict['value'] =int(var.value)
            
        conditions.append(var_dict)
    return conditions
