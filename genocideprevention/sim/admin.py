from genocideprevention.sim.models import *
from django.contrib import admin

admin.site.register(Role)

class StateVariableInline(admin.TabularInline):
    model = StateVariable
    extra = 0
    
class StateRoleChoiceInline(admin.TabularInline):
    model = StateRoleChoice
    extra = 0

class StateChangeInline(admin.TabularInline):
    model = StateChange
    extra = 0
    fk_name = "state"

class StateAdmin(admin.ModelAdmin):
    inlines = [StateVariableInline, StateRoleChoiceInline, StateChangeInline]
      
admin.site.register(State, StateAdmin)

class PlayerInline(admin.TabularInline):
    model = Player
    extra = 4

class GroupAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]

admin.site.register(Group, GroupAdmin)