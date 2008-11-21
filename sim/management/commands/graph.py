from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from optparse import make_option
from genocideprevention.sim.models import *
import random as  rn

class Command(BaseCommand):
    help = 'Graphs the transition states for the game'
    args = '[appname ...]'
    colors = ["#008080", "#0000FF", "#FF00FF", "#008000", "#00FF00", "#800000", "#000080", "#800080", "#FF0000"]

    def recurse_state(self, state):
        if state not in self.states:
            self.states[state] = {}
        
        transitions = StateChange.objects.filter(state=state).order_by('nextState__state_no')
        stack = []
        color = '#' + "".join(["%02x"%rn.randint(50, 200) for x in range(3)])
        
        for transition in transitions:
            if transition.nextState not in self.states[state]:
                self.states[state][transition.nextState] = "foo"
                print '   "%s" -> "%s" [tailport=e, headport=w, color="%s"];' % (transition.state, transition.nextState, self.colors[transition.state.state_no-1])
                stack.append(transition.nextState)
        
        for s in stack:        
            self.recurse_state(s)
            
    def __cluster(self, turn, cluster, label):
        
        print '   subgraph cluster_%s {' % cluster
        print '      style=filled;'
        print '      color=lightgrey;'
        print '      node [style=filled,color=white];'
        # print '      label="%s"' % label
        
        states = State.objects.filter(turn=turn).order_by("state_no")
        for state in states:
            print '      "%s";' % (state)
        
        print '   }'
        print ''
                
    def handle(self, *app_labels, **options):
        from django.db.models import get_app, get_apps, get_models
        
        self.states= {}

        print 'digraph G {'
        print '   "T1_S1_Start" [shape=Mdiamond];'
        print '   rankdir=LR;'
        print '   splines=false;'
        print '   nodesep=.4;'
        print '   node [shape=tripleoctagon];'
        
        self.__cluster(2, 0, "Turn 2")
        self.__cluster(3, 1, "Turn 3")
        self.__cluster(4, 2, "Turn 4")
    
        # iterate the StateChange table
        state = State.objects.get(name='Start', turn=1, state_no=1)

        self.recurse_state(state)
            
        print '}'

