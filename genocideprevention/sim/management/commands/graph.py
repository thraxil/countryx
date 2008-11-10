from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from optparse import make_option
from genocideprevention.sim.models import *

class Command(BaseCommand):
    help = 'Graphs the transition states for the game'
    args = '[appname ...]'

    def recurseState(self, state):
        if state not in self.states:
            self.states[state] = {}
        
        transitions = StateChange.objects.filter(state=state).order_by('nextState__state_no')
        
        for transition in transitions:
            if transition.nextState not in self.states[state]:
                self.states[state][transition.nextState] = "foo"
                print '   "%s" -> "%s"' % (transition.state, transition.nextState)
                self.recurseState(transition.nextState)
                
    def handle(self, *app_labels, **options):
        from django.db.models import get_app, get_apps, get_models

        self.states = {}
        
        print 'digraph unix {'
        print '   size="6,6";'
        print '   node [color=lightblue2, style=filled];'

        # iterate the StateChange table
        state = State.objects.get(name='Start', turn=1, state_no=1)

        self.recurseState(state)
            
        print '}'

