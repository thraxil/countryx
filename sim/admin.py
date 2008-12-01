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

class SectionAdministratorInline(admin.StackedInline):
    model = SectionAdministrator
    extra = 1
    
class SectionAdmin(admin.ModelAdmin):
    inlines = [SectionAdministratorInline]
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

#################################################################################

class FooPlayerForm(forms.ModelForm):
    class Meta:
        model=FooPlayer
                
    def clean_role(self):
        value = self.cleaned_data["role"]
        if not value:
            raise forms.ValidationError('Please select a role.')
        return value
                
    def clean_user(self):
        value = self.cleaned_data["user"]
        if not value:
            raise forms.ValidationError('Please select a user.')
        return value
    
    def clean(self):
        print "FooPlayerForm:clean"
        return self.cleaned_data

class FooGroupForm(forms.ModelForm):
    class Meta:
        model=FooGroup
        
    def clean_name(self):
        print "Cleaning Name"
        value = self.cleaned_data["name"]
        if not value:
            print "Raising Error"
            raise forms.ValidationError('Please enter a group name.')
        return value    
    
    def clean(self):
        """
        Check that roles & users are filled in.
        For some reason, the inline form is not called if no values are filled in
        """
        cleaned_data = self.cleaned_data
        
#        raise forms.ValidationError("Did not send for 'help' in "
 #                       "the subject despite CC'ing yourself.")
        
        return cleaned_data

class FooPlayerInline(admin.TabularInline):
    model = FooPlayer
    max_num = 4
    extra = 4
    form = FooPlayerForm
    
class FooGroupAdmin(admin.ModelAdmin):
    inlines = [FooPlayerInline]
    model = FooPlayer
    extra = 1
    form = FooGroupForm
    
admin.site.register(FooGroup, FooGroupAdmin)


        