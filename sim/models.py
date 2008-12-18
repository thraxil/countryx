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
    <State: T1_S1_Test>
    """
    
    turn = models.IntegerField()
    state_no = models.IntegerField()
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return "T%s_S%s_%s" % (self.turn, self.state_no, self.name)

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

class SectionGroup(models.Model):
    name = models.CharField(max_length=20)
    section = models.ForeignKey(Section)
    
    def __unicode__(self):
        return "%s: Group %s" % (self.section, self.name)
    
def sectiongroup_post_save(sender, instance, signal, *args, **kwargs):
    states = SectionGroupState.objects.filter(group=instance)
    
    if (len(states) < 1):
        # Create the initial state in the SectionGroupState table
        state = State.objects.get(name="Start", turn=1, state_no=1)
        SectionGroupState.objects.create(state=state, group=instance, date_updated=datetime.date.today())
    
models.signals.post_save.connect(sectiongroup_post_save, sender=SectionGroup)
    
class SectionGroupState(models.Model):
    state = models.ForeignKey(State)
    group = models.ForeignKey(SectionGroup)
    date_updated = models.DateTimeField('date updated')
    
    def __unicode__(self):
        return "%s %s" % (self.state, self.date_updated)
        
class SectionGroupPlayer(models.Model):
    user = models.ForeignKey(User)
    group = models.ForeignKey(SectionGroup)
    role = models.ForeignKey(Role)
    
    def __unicode__(self):
        return "%s: [%s, %s]" % (self.user, self.role.name, self.group)
        
class SectionGroupPlayerTurn(models.Model):
    player = models.ForeignKey(SectionGroupPlayer, related_name="%(class)s_related_player")
    state = models.ForeignKey(State)
    choice = models.IntegerField(null=True)
    reasoning = models.TextField(null=True)
    submit_date = models.DateTimeField('final date submitted', null=True)
    feedback = models.TextField(null=True)
    faculty = models.ForeignKey(SectionAdministrator, related_name="%(class)s_related_faculty", null=True)
    feedback_date = models.DateTimeField('feedback submitted', null=True)
    
    def __unicode__(self):
        return "%s: Selected: %s from state %s" % (self.player, self.state.turn, self.choice)
    
    def is_submitted(self):
        return self.submit_date != None