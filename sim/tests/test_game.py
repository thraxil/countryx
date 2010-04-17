from django.test import TestCase, Client
from countryx.sim.models import *
import simplejson
import datetime

class GameTestCases(TestCase):
    fixtures = ["test_data.json"]
    
    def _login(self, client, uname, pwd):
            # Do a fake login via the handy client login fixture
        self.assertTrue(client.login(username=uname, password=pwd))
        
        response = client.get('/sim/')
        self.assertContains(response, uname, status_code=200)
        self.assertTemplateUsed(response, "sim/player_index.html")
        
    def test_game_nochoices(self):
        user = User.objects.get(username='playerA')
        group = SectionGroup.objects.get(name='A', section=Section.objects.get(name='Test'))
        
        self.assertEquals(group.status(), GROUP_STATUS_NOACTION)
        
        self._login(self.client, 'playerA', 'aaaa')
        url = '/sim/player/game/%s/' % group.id
        response = self.client.get(url)
        
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "sim/player_game.html")
        
        ctx = response.context[0]
        self.assertEquals(ctx.get('user'), user)
        self.assertEquals(ctx.get('group'), group)
        
        your_player = ctx.get('you')
        self.assertEquals(your_player['model'], SectionGroupPlayer.objects.get(user=user, group=group))
        
        self.assertEquals(your_player['submit_status'], PLAYER_STATUS_NOACTION)
        self.assertEquals(your_player['saved_turn'], None)
        self.assertEquals(your_player['saved_choice'], None)
        
    def test_game_decisionpending(self):
        self._login(self.client, 'playerA', 'aaaa')
        
        user = User.objects.get(username='playerA')
        group = SectionGroup.objects.get(name='A', section=Section.objects.get(name='Test'))
        current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
        player = SectionGroupPlayer.objects.get(user=user,group=group)
                
        # choose a draft item, assume it's correct, that's checked later
        payload = "groupid=%s&choiceid=1&final=0&reasoning=foobar" % group.id
        self.client.post('/sim/player/choose/', payload, content_type="text/xml")
        
        # now get the game screen
        url = '/sim/player/game/%s/' % group.id
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "sim/player_game.html")
        
        ctx = response.context[0]
        self.assertEquals(ctx.get('user'), user)
        self.assertEquals(ctx.get('group'), group)
        
        your_player = ctx.get('you')
        self.assertEquals(your_player['model'], player)
        
        self.assertEquals(your_player['submit_status'], PLAYER_STATUS_PENDING)
        
        turn = SectionGroupPlayerTurn.objects.get(player=player, turn=current_state.turn)
        self.assertEquals(your_player['saved_turn'], turn)
        self.assertEquals(your_player['saved_choice'], StateRoleChoice.objects.get(state=current_state, role=player.role, choice=turn.choice))
          
    def test_game_finalsubmit(self):
        self._login(self.client, 'playerA', 'aaaa')
        
        user = User.objects.get(username='playerA')
        group = SectionGroup.objects.get(name='A', section=Section.objects.get(name='Test'))
        current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
        player = SectionGroupPlayer.objects.get(user=user,group=group)
                
        # choose a draft item, assume it's correct, that's checked later
        payload = "groupid=%s&choiceid=1&final=1&reasoning=foobar" % (group.id)
        self.client.post('/sim/player/choose/', payload, content_type="text/xml")
        
        # now get the game screen
        url = '/sim/player/game/%s/' % group.id
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "sim/player_game.html")
        
        ctx = response.context[0]
        self.assertEquals(ctx.get('user'), user)
        self.assertEquals(ctx.get('group'), group)
        
        your_player = ctx.get('you')
        self.assertEquals(your_player['model'], player)
        self.assertEquals(your_player['submit_status'], PLAYER_STATUS_SUBMITTED)
        
        turn = SectionGroupPlayerTurn.objects.get(player=player, turn=current_state.turn)
        self.assertEquals(your_player['saved_turn'], turn)
        self.assertEquals(your_player['saved_choice'], StateRoleChoice.objects.get(state=current_state, role=player.role, choice=turn.choice))
               
    def test_ajax_not_loggedin(self):
        c = self.client
        response = c.post('/sim/player/choose/', {'groupid': 1, 'choiceid': 1, 'final': 0, 'reasoning': ''})
        self.assertRedirects(response, expected_url="/accounts/login/?next=/sim/player/choose/", status_code=302, target_status_code=200)
        self.assertEquals(response.template, None)
        self.assertEquals(response.content, '')
        
    def test_choose_savedraft_invalid(self):
        c = self.client
        self._login(c, 'playerA', 'aaaa')
 
        payload = "<?xml version='1.0' encoding='utf-8'?><library><book><title>Blink</title><author>Malcolm Gladwell</author></book></library>"
        response = c.post('/sim/player/choose/', payload, content_type="text/xml")
        self.assertEquals(response.status_code, 404)
    
    def test_choose_savedraft_valid(self):
        c = self.client
        self._login(c, 'playerA', 'aaaa')
        
        group = SectionGroup.objects.get(name='A', section=Section.objects.get(name='Test'))
        payload = "groupid=%s" % group.id
        payload += "&choiceid=1&final=0&reasoning=Enter%20your%20reasoning%20here"
        response = c.post('/sim/player/choose/', payload, content_type="text/xml")
        
        doc = simplejson.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(doc['result'], 1)
        
        # verify my choice was saved in the database
        current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
        user = User.objects.get(username='playerA')
        player = group.sectiongroupplayer_set.get(user__id=user.id)
        turn = SectionGroupPlayerTurn.objects.get(player=player, turn=current_state.turn)
        self.assertEquals(turn.choice, 1)
        self.assertEquals(turn.submit_date, None)
        self.assertEquals(turn.reasoning, 'Enter your reasoning here')
        
    def test_choose_submit(self):
        c = self.client
        self._login(c, 'playerA', 'aaaa')
        
        group = SectionGroup.objects.get(name='A', section=Section.objects.get(name='Test'))
        payload = "groupid=%s" % group.id
        payload += "&choiceid=1&final=1&reasoning=Enter%20your%20reasoning%20here"
        response = c.post('/sim/player/choose/', payload, content_type="text/xml")
        
        doc = simplejson.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(doc['result'], 2)
        
        # verify my choice was saved in the database
        current_state = group.sectiongroupstate_set.order_by('date_updated')[0].state
        user = User.objects.get(username='playerA')
        player = group.sectiongroupplayer_set.get(user__id=user.id)
        turn = SectionGroupPlayerTurn.objects.get(player=player, turn=current_state.turn)
        self.assertEquals(turn.choice, 1)
        self.assert_(turn.submit_date != None)
        self.assertEquals(turn.reasoning, 'Enter your reasoning here')
        
        # now, try it again, an error should be thrown this time.
        payload = "groupid=%s" % group.id
        payload += "&choiceid=1&final=0&reasoning=Trying%20Again"
        response = c.post('/sim/player/choose/', payload, content_type="text/xml")
        
        doc = simplejson.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(doc['result'], 0)
        
        # verify object is unchanged
        turn = SectionGroupPlayerTurn.objects.get(player=player, turn=current_state.turn)
        self.assertEquals(turn.choice, 1)
        self.assert_(turn.submit_date != None)
        self.assertEquals(turn.reasoning, 'Enter your reasoning here')       
        
    def test_faculty_reset(self):
        c = self.client
        self._login(c, 'playerA', 'aaaa')
        
        section = Section.objects.get(name='Test')
        url = '/sim/faculty/reset/%d/' % section.id
        response = c.post(url, '', content_type="text/xml")
        
        doc = simplejson.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(doc['message'], 'Access denied')
        
        admin = User(username="admin", is_superuser="true")
        admin.set_password("admin")
        admin.save()
        
        c.get('/sim/logout/')
        self._login(c, 'admin', 'admin')
        
        response = c.post(url, '', content_type="text/xml")
        doc = simplejson.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertTrue(len(doc['turn1']) > 0)
        
        
        
                
