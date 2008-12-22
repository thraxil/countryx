from django.test import TestCase, Client
from genocideprevention.sim.models import *
import simplejson
import datetime

class ModelTestCases(TestCase):
    fixtures = ["test_data.json"]
    
    def test_group_status_noaction(self):
        # update the data manually to setup this test
        group = SectionGroup.objects.get(id=1)
        self.assertEquals(GROUP_STATUS_NOACTION, group.status())
            
    def test_group_status_pending_submitted(self):
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
        