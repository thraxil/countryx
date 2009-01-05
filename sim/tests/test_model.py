from django.test import TestCase, Client
from genocideprevention.sim.models import *
import simplejson
import datetime

class ModelTestCases(TestCase):
    fixtures = ["test_data.json"]
    
    def _test_group_status_noaction(self):
        # update the data manually to setup this test
        group = SectionGroup.objects.get(id=1)
        self.assertEquals(GROUP_STATUS_NOACTION, group.status())
            
    def _test_group_status_pending_submitted(self):
        # update the data manually to setup this test
        group = SectionGroup.objects.get(id=1)
        current_state = group.sectiongroupstate_set.latest().state
        players = SectionGroupPlayer.objects.filter(group=group)
        
        count = 0
        for player in players:
            turn = SectionGroupPlayerTurn.objects.create(player=player, state=current_state, choice=1, submit_date=datetime.datetime.now(), reasoning="foobar")
            if count < 3:
                self.assertEquals(GROUP_STATUS_PENDING, group.status())
            else:
                self.assertEquals(GROUP_STATUS_SUBMITTED, group.status())
            count += 1
            
    def _test_player_status(self):
        group = SectionGroup.objects.get(id=2)
        player = SectionGroupPlayer.objects.get(user__username='playerE')
        
        states = group.sectiongroupstate_set.all().order_by('state__turn')
        
        self.assertEquals(PLAYER_STATUS_SUBMITTED, player.status(states[0].state))
        self.assertEquals(PLAYER_STATUS_NOACTION, player.status(states[1].state))
        
        # create a draft for states[1]
        turn = SectionGroupPlayerTurn.objects.create(player=player, state=states[1].state, choice=1, reasoning="foobar")
        self.assertEquals(PLAYER_STATUS_PENDING, player.status(states[1].state))
        
        turn.submit_date=datetime.datetime.now()
        turn.save()
        self.assertEquals(PLAYER_STATUS_SUBMITTED, player.status(states[1].state))
        
    def test_player_current_status(self):
        group = SectionGroup.objects.get(name='B')
        player = SectionGroupPlayer.objects.get(user__username='playerA')
        
        self.assertEquals(PLAYER_STATUS_NOACTION, player.current_status())
        
    #def test_section_current_turn(self):
        
        
            
        