from django.test import TestCase, Client
from genocideprevention.sim.models import *
import simplejson

class GameTestCases(TestCase):
    fixtures = ["test_data.json"]
    
    def _login(self, client, uname, pwd):
            # Do a fake login via the handy client login fixture
        self.assert_(client.login(username=uname, password=pwd))
        
        response = client.get('/sim/')
        self.assertContains(response, "Welcome", status_code=200)
        self.assertTemplateUsed(response, "sim/player_index.html")
        
    def _test_ajax_not_loggedin(self):
        c = self.client
        response = c.post('/sim/player/choose/', {'groupid': 1, 'choiceid': 1, 'final': 0, 'reasoning': ''})
        self.assertRedirects(response, expected_url="/accounts/login/?next=/sim/player/choose/", status_code=302, target_status_code=200)
        self.assertEquals(response.template, None)
        self.assertEquals(response.content, '')
        
    def _test_choose_savedraft_invalid(self):
        c = self.client
        self._login(c, 'playerA', 'aaaa')
        
        payload = "<?xml version='1.0' encoding='utf-8'?><library><book><title>Blink</title><author>Malcolm Gladwell</author></book></library>"
            
        response = c.post('/sim/player/choose/', payload, content_type="text/xml")
        
        doc = simplejson.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(doc['result'], 0)
    
    def _test_choose_savedraft_valid(self):
        c = self.client
        self._login(c, 'playerA', 'aaaa')
        
        payload = "groupid=1&choiceid=1&final=0&reasoning=Enter%20your%20reasoning%20here"
            
        response = c.post('/sim/player/choose/', payload, content_type="text/xml")
        
        doc = simplejson.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(doc['result'], 1)
        
        # verify my choice was saved in the database
        group = SectionGroup.objects.get(id=1)
        current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
        user = User.objects.get(username='playerA')
        player = group.sectiongroupplayer_set.get(user__id=user.id)
        turn = SectionGroupPlayerTurn.objects.get(player=player, state=current_state)
        self.assertEquals(turn.choice, 1)
        self.assertEquals(turn.submit_date, None)
        self.assertEquals(turn.reasoning, 'Enter your reasoning here')
        
    def test_choose_submit(self):
        c = self.client
        self._login(c, 'playerA', 'aaaa')
        
        payload = "groupid=1&choiceid=1&final=1&reasoning=Enter%20your%20reasoning%20here"
            
        response = c.post('/sim/player/choose/', payload, content_type="text/xml")
        
        doc = simplejson.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(doc['result'], 1)
        
        # verify my choice was saved in the database
        group = SectionGroup.objects.get(id=1)
        current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
        user = User.objects.get(username='playerA')
        player = group.sectiongroupplayer_set.get(user__id=user.id)
        turn = SectionGroupPlayerTurn.objects.get(player=player, state=current_state)
        self.assertEquals(turn.choice, 1)
        self.assert_(turn.submit_date != None)
        self.assertEquals(turn.reasoning, 'Enter your reasoning here')
        
        # now, try it again, an error should be thrown this time.
        payload = "groupid=1&choiceid=1&final=0&reasoning=Trying%20Again"
        response = c.post('/sim/player/choose/', payload, content_type="text/xml")
        
        doc = simplejson.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(doc['result'], 0)
        
        # verify object is unchanged
        turn = SectionGroupPlayerTurn.objects.get(player=player, state=current_state)
        self.assertEquals(turn.choice, 1)
        self.assert_(turn.submit_date != None)
        self.assertEquals(turn.reasoning, 'Enter your reasoning here')