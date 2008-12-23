from django.db import models, connection
from django.contrib.auth.models import User
from django.db.models import signals
from django.dispatch import dispatcher
import datetime

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
        myfield = StateChange._meta.get_field('nextState').column
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
            StateChange._meta.get_field('nextState').column,
            extra
            )
    
    def from_count(self,extra=''):
        return self._countedges(
            StateChange._meta.get_field('nextState').column,
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
    nextState = models.ForeignKey(State, related_name="%(class)s_related_next")
    
    def __unicode__(self):
        return "[%s] P=%s E%s R=%s O=%s >> [%s]" % (self.state, self.president, self.envoy, self.regional, self.opposition, self.nextState)

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

    def __unicode__(self):
        return "%s %s %s" % (self.name, self.term, self.year)

class SectionAdministrator(models.Model):
    user = models.ForeignKey(User)
    section = models.ForeignKey(Section)
    
    def __unicode__(self):
        return "%s" % (self.user)
    
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
            
    def maybeUpdateState(self):
        # are all my players submitted for the current turn?
        current_state = sectiongroupstate_set.latest().state
        players = SectionGroupPlayerTurn.objects.filter(player__group=self, state=current_state, submit_date__isnull=False)
        if players.count() == 4:
            # everyone has submitted their answers for this turn.
            # update the game state, and let people advance.
            print "not doing anything here yet"
    
class SectionGroupState(models.Model):
    state = models.ForeignKey(State)
    group = models.ForeignKey(SectionGroup)
    date_updated = models.DateTimeField('date updated')
    class Meta:
        get_latest_by = 'date_updated'
    
    def __unicode__(self):
        return "%s %s" % (self.state, self.date_updated)
    
    def status(self):
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

   
    def status(self, current_state):
        action = PLAYER_STATUS_NOACTION
        
        if (self.sectiongroupplayerturn_related_player.all().count() > 0):
            try:
                turn = self.sectiongroupplayerturn_related_player.get(state=current_state)
                if turn.submit_date:
                    action = PLAYER_STATUS_SUBMITTED
                else:
                    action = PLAYER_STATUS_PENDING
            except SectionGroupPlayerTurn.DoesNotExist:
                pass
                 
        return action
        
class SectionGroupPlayerTurn(models.Model):
    player = models.ForeignKey(SectionGroupPlayer, related_name="%(class)s_related_player")
    state = models.ForeignKey(State)
    choice = models.IntegerField(null=True)
    reasoning = models.TextField(null=True)
    submit_date = models.DateTimeField('final date submitted', null=True)
    feedback = models.TextField(null=True)
    faculty = models.ForeignKey(SectionAdministrator, related_name="%(class)s_related_faculty", null=True)
    feedback_date = models.DateTimeField('feedback submitted', null=True)
    class Meta:
        get_latest_by = 'submit_date'
    
    def __unicode__(self):
        return "%s: Selected: %s from state %s" % (self.player, self.state.turn, self.choice)
    
    def is_submitted(self):
        return self.submit_date != None

        