from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.name

class State(models.Model):
    turn = models.IntegerField()
    state_no = models.IntegerField()
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return "T%s_S%s_%s" % (self.turn, self.state_no, self.name)
    
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
    
    
