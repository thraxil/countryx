from genocideprevention.sim.models import *
from django.contrib import admin
from django import forms

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

#################################################################################

class SectionTurnDatesInline(admin.StackedInline):
    model = SectionTurnDates
    max_num = 1
    extra = 1

class SectionAdministratorInline(admin.StackedInline):
    model = SectionAdministrator
    extra = 1
    
class SectionAdmin(admin.ModelAdmin):
    inlines = [SectionAdministratorInline, SectionTurnDatesInline]
    model = Section

admin.site.register(Section, SectionAdmin)

#################################################################################

class SectionGroupPlayerInline(admin.TabularInline):
    model = SectionGroupPlayer
    max_num = 4
    extra = 4
    
class SectionGroupStateInline(admin.StackedInline):
    model = SectionGroupState
    extra = 1
    
class SectionGroupAdmin(admin.ModelAdmin):
    inlines = [SectionGroupPlayerInline, SectionGroupStateInline]
    model = SectionGroup
    extra = 1
    
admin.site.register(SectionGroup, SectionGroupAdmin)

        