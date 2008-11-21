from django.db import models, connection

class Role(models.Model):
    """
    A role allows a player to assume a specific persona in the game.
    Roles are associated with State Changes and Role Choices

    """
    
    name = models.CharField(max_length=20, unique=True)

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
            metadata['influence_from'][role] = self.influence(role, self.from_count, metadata['from'])
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
    value = models.CharField(max_length=1500)
    
    def __unicode__(self):
        return "[%s] %s: %s" % (self.state, self.name, self.value)
    
class StateRoleChoice(models.Model):
    state = models.ForeignKey(State)
    role = models.ForeignKey(Role)
    choice = models.IntegerField()
    desc = models.CharField(max_length=250)

    def __unicode__(self):
        return "[%s] %s: %s. %s" % (self.state, self.role, self.choice, self.desc)
    
class Group(models.Model):
    name = models.CharField(max_length=20)
    current_state = models.ForeignKey(State)
    
    def __unicode__(self):
        return "%s" % (self.name)
    
class Player(models.Model):
    group = models.ForeignKey(Group)
    uni = models.CharField(max_length=10)
    role = models.ForeignKey(Role)
    
    def __unicode__(self):
        return "%s: [%s, %s]" % (self.uni, self.role.name, self.group)
    
class PlayerTurn(models.Model):
    player = models.ForeignKey(Player)
    state = models.ForeignKey(State)
    choice = models.IntegerField()
    date_submitted = models.DateTimeField('date submitted')

    def __unicode__(self):
        return "%s: Selected: %s from state %s" % (self.player, self.state.turn, self.choice)
    
    
