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
    
    def init_google_client(self, email, password):
        
        #initialize the spreadsheet service
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()

        if (not email or email == ''):
            print "Please enter a valid email address"
            return False
        if (not password or password == ''):
            print "Please enter a valid password"
            return False
        
        # initialize the google library stuff
        self.gd_client.email = email
        self.gd_client.password = password
        self.gd_client.ProgrammaticLogin()
        return True
        
    def prepare_database(self):
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
        self.get_or_create_role('President')
        self.get_or_create_role('FirstWorldEnvoy')
        self.get_or_create_role('SubRegionalRep')
        self.get_or_create_role('OppositionLeadership')   
            
    def get_or_create_state(self, text):
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
    
    def get_or_create_role(self, roleName):
        try:
            role = Role.objects.get(name=roleName)
        except Role.DoesNotExist:
            role = Role.objects.create(name=roleName)
        return role
            
    def process_conditions(self, sheetKey, worksheetId, state):
        print "process conditions for state: %s" % state
        feed = self.gd_client.GetListFeed(sheetKey, worksheetId)
                
        for i, entry in enumerate(feed.entry):
            #each row has at least two key values: name, value
            #these will each translate into a StateVariable object
            var = StateVariable()
            var.state = state
            var.value = entry.custom["value"].text
            var.name = entry.custom["name"].text
            if (var.name):
                var.value = var.value.replace("\n", "<br /><br />")
                var.save()
                print "%s" % (var)
        
    def process_choices(self, sheetKey, worksheetId, state):
        print "process choices for state: %s" % state
        feed = self.gd_client.GetListFeed(sheetKey, worksheetId)
        choices = []
        role = None
        
        for i, entry in enumerate(feed.entry):
            #each row has at least three viable key values: role, choiceno, desc
            #these will each translate into a StateRoleChoice object
            if (entry.custom["role"].text):
                roleName = entry.custom["role"].text
                roleName = roleName.replace('(', '')
                roleName = roleName.replace(')', '')
                roleName = roleName.replace(' ', '')
                roleName = roleName.replace('-', '')
                role = Role.objects.get(name=roleName)
                print "Choices for role %s" % role
                
            choiceno = entry.custom["choiceno"].text
            choicedesc = entry.custom["desc"].text
            if (role and choiceno and choicedesc):
                c = StateRoleChoice()
                c.state = state
                c.choice = choiceno
                c.desc = choicedesc.replace('\n', '')
                c.role = role
                c.save() 
                print '%s' % c
            
    def process_transitions(self, sheetKey, worksheetId, state): 
        print "process transitions for state %s" % state 
        feed = self.gd_client.GetListFeed(sheetKey, worksheetId)
        
        for i, entry in enumerate(feed.entry):
            if (entry.custom["resultingstate"].text):
                #each row has 5 key values, P, E, R, O (roles) and the resulting state
                #these will each translate into a StateRoleChoice object
                transition = StateChange()
                transition.state = state
                transition.envoy = entry.custom["e"].text
                transition.opposition = entry.custom["o"].text
                transition.president = entry.custom["p"].text
                transition.regional = entry.custom["r"].text
                transition.nextState = self.get_or_create_state(entry.custom["resultingstate"].text)
                transition.save()
                print "%s" % transition
               
    def process_worksheets(self, sheetKey, state):  
        feed = self.gd_client.GetWorksheetsFeed(sheetKey)
        
        if (len(feed.entry) <> 3):
            print "%s does not have three required worksheets. Skipping..." % state
            return
        
        for i, entry in enumerate(feed.entry):
            id_parts = entry.id.text.split('/')
            worksheetId = id_parts[len(id_parts) - 1]
    
            if (entry.title.text == "Conditions"):
                self.process_conditions(sheetKey, worksheetId, state)
            elif (entry.title.text == "Choices"):
                self.process_choices(sheetKey, worksheetId, state)
            elif (entry.title.text == "Transitions"):
                self.process_transitions(sheetKey, worksheetId, state)  
        
    def process_spreadsheets(self):
        feed = self.gd_client.GetSpreadsheetsFeed()
        for i, entry in enumerate(feed.entry):
            match = re.search("t\d{1}_s\d{1}_*", entry.title.text, re.IGNORECASE)
            if (match):
                
                #parse out a new state object
                state = self.get_or_create_state(entry.title.text)
                
                # parse out the sheet's identifying key
                # this is a bit of a hack, could use an XML parser to make this nicer
                id_parts = entry.id.text.split('/')
                key = id_parts[len(id_parts) - 1]   
                              
                #process each of the three expected worksheets
                print "Processing spreadsheet %s" % state 
                self.process_worksheets(key, state)
        
    def handle(self, *app_labels, **options):
        from django.db.models import get_app, get_apps, get_models
        
        args = 'Usage: python manage.py import --user user --pwd password]'
        
        if (not self.init_google_client(options.get('user'), options.get('pwd'))):
            print args
            return
        else:
            print "Retrieving data for: ", self.gd_client.email
    
        # delete the old data, and make sure the roles are created
        self.prepare_database()
        
        # process the spreadsheets
        self.process_spreadsheets()
    