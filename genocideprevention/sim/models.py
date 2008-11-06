from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=20)

    def __unicode__(self):
        return self.name

class State(models.Model):
    turn = models.IntegerField()
    state_no = models.IntegerField()
    name = models.CharField(max_length=40)

    def __unicode__(self):
        return "S%s_T%s_%s" % (self.state_no, self.turn, self.name)
    
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
    value = models.CharField(max_length=1000)
    
    def __unicode__(self):
        return "[%s] %s: %s" % (self.state, self.name, self.value)
    
class StateRoleChoice(models.Model):
    state = models.ForeignKey(State)
    role = models.ForeignKey(Role)
    choice = models.IntegerField()
    desc = models.CharField(max_length=250)

    def __unicode__(self):
        return "[%s] %s: %s. %s" % (self.state, self.role, self.choice, self.desc)
