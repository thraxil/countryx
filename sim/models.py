from django.db import models, connection
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import dispatcher
import datetime, random

class Role(models.Model):
    """
    A role allows a player to assume a specific persona in the game.
    Roles are associated with State Changes and Role Choices
    """
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField()

    def __unicode__(self):
        return self.name

class State(models.Model):
    """
    A state represents a current country condition. Each state has a set of 
    representative values (violence, esteem, etc), choices that each player
    role can follow and the list of states these choices can lead to.
    
    #Create a state
    >>> state = State.objects.create(name="Test", turn=1, state_no=1)
    >>> state
    <State: Turn 1: Test>
    """
    
    turn = models.IntegerField()
    state_no = models.IntegerField()
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return "Turn %s: %s" % (self.turn, self.name)

    def _countedges(self,myfield,otherfield,extra=''):
        tablename = StateChange._meta.db_table
        cursor = connection.cursor()
        cursor.execute('SELECT "%s",count("%s") FROM "%s" WHERE "%s"=%d %s GROUP BY "%s"' % (
            otherfield,otherfield, tablename, myfield,self.id, extra, otherfield
            ))
        return cursor.rowcount
    
    def influence_from(self, role):
        tablename = StateChange._meta.db_table
        myfield = StateChange._meta.get_field('next_state').column
        otherfield = StateChange._meta.get_field('state').column
        cursor = connection.cursor()
        cursor.execute('SELECT "%s",count("%s") FROM "%s" WHERE "%s"=%d %s GROUP BY "%s"' % (
            otherfield,otherfield, tablename, myfield,self.id, '', otherfield
            ))
        rv = []
        for row in cursor.fetchall():
            cursor.execute('SELECT count("%s") FROM "%s" WHERE "%s"=%d AND "%s"=%d GROUP BY "%s"' % (
                role, tablename, myfield,self.id, otherfield,row[0],  role
                ))
            rv.append(3-cursor.rowcount)
        return rv
            
    def to_count(self,extra=''):
        return self._countedges(
            StateChange._meta.get_field('state').column,
            StateChange._meta.get_field('next_state').column,
            extra
            )
    
    def from_count(self,extra=''):
        return self._countedges(
            StateChange._meta.get_field('next_state').column,
            StateChange._meta.get_field('state').column,
            extra
            )
    
    def influence(self,role,func,count):
        rv = []
        for choice in range(1,4):
            rv.append(count-func('AND %s=%d' % (role,choice)))
        return rv
    
    def edge_metadata(self):
        metadata = {'to':self.to_count(),
                    'from':self.from_count(),
                    'influence_from':{},
                    'influence_to':{}}
        for role in ('president','envoy','regional','opposition'):
            #metadata['influence_from'][role] = metadata['from']*3 - self.influence(role,self.from_count)
            #metadata['influence_to'][role] = metadata['to']*3 - self.influence(role,self.to_count)
            metadata['influence_from'][role] = self.influence_from(role)
            metadata['influence_to'][role] = self.influence(role, self.to_count, metadata['to'])
            
        return metadata
    
class StateChange(models.Model):
    state = models.ForeignKey(State, related_name="%(class)s_related_current")
    president = models.IntegerField()
    envoy = models.IntegerField()
    regional = models.IntegerField()
    opposition = models.IntegerField()
    next_state = models.ForeignKey(State, related_name="%(class)s_related_next")
    
    def __unicode__(self):
        return "[%s] P=%s E%s R=%s O=%s >> [%s]" % (self.state, self.president, self.envoy, self.regional, self.opposition, self.next_state)

class StateVariable(models.Model):
    state = models.ForeignKey(State)
    name = models.CharField(max_length=20)
    value = models.TextField()
        
    def __unicode__(self):
        return "[%s] %s: %s" % (self.state, self.name, self.value)
        
class StateRoleChoice(models.Model):
    state = models.ForeignKey(State)
    role = models.ForeignKey(Role)
    choice = models.IntegerField()
    desc = models.CharField(max_length=250)

    def __unicode__(self):
        return "[%s] %s: %s. %s" % (self.state, self.role, self.choice, self.desc)

###############################################################################
###############################################################################

class Section(models.Model):
    name = models.CharField(max_length=20)
    term = models.CharField(max_length=20)
    year = models.IntegerField()
    created_date = models.DateTimeField('created_date')

    def __unicode__(self):
        return "%s %s %s" % (self.name, self.term, self.year)
    
    def current_turn(self):
        turn_dates = SectionTurnDates.objects.get(section=self)
        if (turn_dates.turn1 > datetime.datetime.now()):
           return 1
        elif (turn_dates.turn2 == None or turn_dates.turn2 > datetime.datetime.now()):
           return 2
        elif (turn_dates.turn3 == None or turn_dates.turn3 > datetime.datetime.now()):
           return 3
       
        return -1
    
    def current_turn_close_date(self):
        turn_dates = SectionTurnDates.objects.get(section=self)
        if (turn_dates.turn1 > datetime.datetime.now()):
           return turn_dates.turn1
        elif (turn_dates.turn2 == None or turn_dates.turn2 > datetime.datetime.now()):
           return turn_dates.turn2
        elif (turn_dates.turn3 == None or turn_dates.turn3 > datetime.datetime.now()):
           return turn_dates.turn3
        
        return turn_dates.turn1  
     
class SectionAdministrator(models.Model):
    user = models.ForeignKey(User)
    section = models.ForeignKey(Section)
    
    def __unicode__(self):
        return "%s" % (self.user)

class SectionTurnDates(models.Model):
    section = models.ForeignKey(Section)
    turn1 = models.DateTimeField('turn1')
    turn2 = models.DateTimeField('turn2', null=True)
    turn3 = models.DateTimeField('turn3', null=True)

    def __unicode__(self):
        return "%s %s %s %s" % (self.turn1, self.turn2, self.turn3)
        
###############################################################################
###############################################################################

GROUP_PLAYER_COUNT = 4

GROUP_STATUS_NOACTION = 1
GROUP_STATUS_PENDING =  2   
GROUP_STATUS_SUBMITTED = 4

class SectionGroup(models.Model):
    name = models.CharField(max_length=20)
    section = models.ForeignKey(Section)
    
    def __unicode__(self):
        return "%s: Group %s" % (self.section, self.name)
    
    def status(self):
        return self.sectiongroupstate_set.latest().status()
    
    def force_response_all_players(self):
        random.seed(None)
        state = self.sectiongroupstate_set.latest().state
        players = SectionGroupPlayer.objects.filter(group=self)
        
        for player in players:
            # create or update the player's choice
            try:
                #check to see if player has a "draft" saved. Use this if possible.
                player_response = SectionGroupPlayerTurn.objects.get(player=player, turn=state.turn)
                if (player_response.submit_date == None):
                    player_response.submit_date = datetime.datetime.now()
                    player_response.save()
            except:
               # player has no choice saved
               player_response = SectionGroupPlayerTurn.objects.create(player=player, turn=state.turn)
               player_response.choice = random.randint(1,3)
               player_response.submit_date = datetime.datetime.now()
               player_response.save() 
    
    def update_state(self):
        state = self.sectiongroupstate_set.latest().state
        president = SectionGroupPlayerTurn.objects.get(player__role__name='President', player__group=self, turn=state.turn, submit_date__isnull=False)
        regional = SectionGroupPlayerTurn.objects.get(player__role__name='SubRegionalRep', player__group=self, turn=state.turn, submit_date__isnull=False)
        opposition = SectionGroupPlayerTurn.objects.get(player__role__name='OppositionLeadership', player__group=self, turn=state.turn, submit_date__isnull=False)
        envoy = SectionGroupPlayerTurn.objects.get(player__role__name='FirstWorldEnvoy', player__group=self, turn=state.turn, submit_date__isnull=False)
                   
        try:                     
            next_state = StateChange.objects.get(state=state, president=president.choice, envoy=envoy.choice, regional=regional.choice, opposition=opposition.choice).next_state
            SectionGroupState.objects.create(state=next_state, group=self, date_updated=datetime.datetime.now())
        except:
            pass
            
class SectionGroupState(models.Model):
    state = models.ForeignKey(State)
    group = models.ForeignKey(SectionGroup)
    date_updated = models.DateTimeField('date updated')
    class Meta:
        get_latest_by = 'date_updated'
    
    def __unicode__(self):
        return "%s %s" % (self.state, self.date_updated)
    
    def status(self):
        if (self.state.turn == 4):
            return GROUP_STATUS_SUBMITTED
        
        status = 0
        players = self.group.sectiongroupplayer_set.all()
        for player in players:
            status += player.status(self.state)
            
        if (status == PLAYER_STATUS_NOACTION * GROUP_PLAYER_COUNT):
            return GROUP_STATUS_NOACTION
        elif (status == PLAYER_STATUS_SUBMITTED * GROUP_PLAYER_COUNT): 
            return GROUP_STATUS_SUBMITTED
        else:
            return GROUP_STATUS_PENDING

PLAYER_STATUS_NOACTION  = 1
PLAYER_STATUS_PENDING   = 2
PLAYER_STATUS_SUBMITTED = 4
        
class SectionGroupPlayer(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(SectionGroup)
    role = models.ForeignKey(Role)
    
    def __unicode__(self):
        return "%s: [%s, %s]" % (self.user, self.role.name, self.group)

    def current_status(self):
        current_state = self.group.sectiongroupstate_set.latest().state
        return self.status(current_state)
   
    def status(self, current_state):
        action = PLAYER_STATUS_NOACTION
        
        if (self.sectiongroupplayerturn_related_player.all().count() > 0):
            try:
                turn = self.sectiongroupplayerturn_related_player.get(turn=current_state.turn)
                if turn.submit_date:
                    action = PLAYER_STATUS_SUBMITTED
                else:
                    action = PLAYER_STATUS_PENDING
            except SectionGroupPlayerTurn.DoesNotExist:
                pass
                 
        return action
        
class SectionGroupPlayerTurn(models.Model):
    player = models.ForeignKey(SectionGroupPlayer, related_name="%(class)s_related_player")
    turn = models.IntegerField()
    choice = models.IntegerField(null=True)
    reasoning = models.TextField(null=True)
    submit_date = models.DateTimeField('final date submitted', null=True)
    feedback = models.TextField(null=True)
    faculty = models.ForeignKey(SectionAdministrator, related_name="%(class)s_related_faculty", null=True)
    feedback_date = models.DateTimeField('feedback submitted', null=True)
    
    class Meta:
        get_latest_by = 'submit_date'
    
    def __unicode__(self):
        return "%s: Turn: %s Selected: %s" % (self.player, self.turn, self.choice)
    
    def is_submitted(self):
        return self.submit_date != None

        