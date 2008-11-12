from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from optparse import make_option
from genocideprevention.sim.models import *
try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import getopt
import sys
import string
import re
from psycopg2 import IntegrityError

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--user', dest='user', help='GMail user id'),
        make_option('--pwd', dest='pwd', help='GMail password'),
    )
    
    help = 'Import base game data from Google spreadsheets'
    
    def __initGoogleDataClient(self, email, password):
        
        #initialize the spreadsheet service
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()

        if (email == None or email == ''):
            print "Please enter a valid email address"
            return False
        if (password == None or password == ''):
            print "Please enter a valid password"
            return False
        
        # initialize the google library stuff
        self.gd_client.email = email
        self.gd_client.password = password
        self.gd_client.ProgrammaticLogin()
        return True
        
    def __prepareDatabase(self):
        # delete old data from the tables
        print "Deleting old simulation data..."
        StateChange.objects.all().delete()
        print "   StateChange deleted"
        StateRoleChoice.objects.all().delete()
        print "   StateRoleChoice deleted"
        StateVariable.objects.all().delete()
        print "   StateVariable deleted"
        State.objects.all().delete()
        print "   States deleted"
        
        # setup required roles
        self.__getOrCreateRole('President')
        self.__getOrCreateRole('FirstWorldEnvoy')
        self.__getOrCreateRole('SubRegionalRep')
        self.__getOrCreateRole('OppositionLeadership')   
            
    def __getOrCreateState(self, text):
        substrings = text.split("_")
                
        name = substrings[2].replace('\n', '')
        name = name.rstrip(' ')
        state_no = substrings[1][1]
        turn = substrings[0][1]
        
        try: 
            state = State.objects.get(name=name, state_no=state_no, turn=turn)
        except State.DoesNotExist:
            state = State.objects.create(name=name, state_no=state_no, turn=turn)
            print "Creating State: %s" % (state)
        
        return state
    
    def __getOrCreateRole(self, roleName):
        try:
            role = Role.objects.get(name=roleName)
        except Role.DoesNotExist:
            role = Role.objects.create(name=roleName)
        return role
            
    def processConditions(self, sheetKey, worksheetId, state):
        print "process conditions for state: %s" % state
        feed = self.gd_client.GetListFeed(sheetKey, worksheetId)
                
        for i, entry in enumerate(feed.entry):
            #each row has at least two key values: name, value
            #these will each translate into a StateVariable object
            var = StateVariable()
            var.state = state
            var.value = entry.custom["value"].text
            var.name = entry.custom["name"].text
            if (var.name <> None):
                var.save()
                print "%s" % (var)
        
    def processChoices(self, sheetKey, worksheetId, state):
        print "process choices for state: %s" % state
        feed = self.gd_client.GetListFeed(sheetKey, worksheetId)
        choices = []
        role = None
        
        for i, entry in enumerate(feed.entry):
            #each row has at least three viable key values: role, choiceno, desc
            #these will each translate into a StateRoleChoice object
            if (entry.custom["role"].text <> None):
                roleName = entry.custom["role"].text
                roleName = roleName.replace('(', '')
                roleName = roleName.replace(')', '')
                roleName = roleName.replace(' ', '')
                roleName = roleName.replace('-', '')
                role = Role.objects.get(name=roleName)
                print "Choices for role %s" % role
                
            choiceno = entry.custom["choiceno"].text
            choicedesc = entry.custom["desc"].text
            if (role <> None and choiceno <> None and choicedesc <> None):
                c = StateRoleChoice()
                c.state = state
                c.choice = choiceno
                c.desc = choicedesc.replace('\n', '')
                c.role = role
                c.save() 
                print '%s' % c
            
    def processTransitions(self, sheetKey, worksheetId, state): 
        print "process transitions for state %s" % state 
        feed = self.gd_client.GetListFeed(sheetKey, worksheetId)
        
        for i, entry in enumerate(feed.entry):
            if (entry.custom["resultingstate"].text <> None):
                #each row has 5 key values, P, E, R, O (roles) and the resulting state
                #these will each translate into a StateRoleChoice object
                transition = StateChange()
                transition.state = state
                transition.envoy = entry.custom["e"].text
                transition.opposition = entry.custom["o"].text
                transition.president = entry.custom["p"].text
                transition.regional = entry.custom["r"].text
                transition.nextState = self.__getOrCreateState(entry.custom["resultingstate"].text)
                transition.save()
                print "%s" % transition
               
    def processWorksheets(self, sheetKey, state):  
        feed = self.gd_client.GetWorksheetsFeed(sheetKey)
        
        if (len(feed.entry) <> 3):
            print "%s does not have three required worksheets. Skipping..." % state
            return
        
        for i, entry in enumerate(feed.entry):
            id_parts = entry.id.text.split('/')
            worksheetId = id_parts[len(id_parts) - 1]
    
            if (entry.title.text == "Conditions"):
                self.processConditions(sheetKey, worksheetId, state)
            elif (entry.title.text == "Choices"):
                self.processChoices(sheetKey, worksheetId, state)
            elif (entry.title.text == "Transitions"):
                self.processTransitions(sheetKey, worksheetId, state)  
        
    def processSpreadsheets(self):
        feed = self.gd_client.GetSpreadsheetsFeed()
        for i, entry in enumerate(feed.entry):
            match = re.search("t\d{1}_s\d{1}_*", entry.title.text, re.IGNORECASE)
            if (match):
                
                #parse out a new state object
                state = self.__getOrCreateState(entry.title.text)
                
                # parse out the sheet's identifying key
                # this is a bit of a hack, could use an XML parser to make this nicer
                id_parts = entry.id.text.split('/')
                key = id_parts[len(id_parts) - 1]   
                              
                #process each of the three expected worksheets
                print "Processing spreadsheet %s" % state 
                self.processWorksheets(key, state)
        
    def handle(self, *app_labels, **options):
        from django.db.models import get_app, get_apps, get_models
        
        args = 'Usage: python manage.py import --user user --pwd password]'
        
        if (not self.__initGoogleDataClient(options.get('user'), options.get('pwd'))):
            print args
            return
        else:
            print "Retrieving data for: ", self.gd_client.email
    
        # delete the old data, and make sure the roles are created
        self.__prepareDatabase()
        
        # process the spreadsheets
        self.processSpreadsheets()
    