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
    
class i:

    def __init__(self):
        #initialize the spreadsheet service
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        
    def __getOrCreateState(self, text):
        substrings = text.split("_")
                
        name = substrings[2]
        state_no = substrings[0][1]
        turn = substrings[1][1]
        
        try:
            state = State.objects.get(name=name, state_no=state_no, turn=turn)
        except State.DoesNotExist:
            state = State()
            state.name = name
            state.state_no = state_no
            state.turn = turn
            state.save()
            print "Creating State: %s" % (state)
        
        return state
                
    def processConditions(self, sheetKey, worksheetId, state):
        print "process conditions for state: %s" % state
        feed = self.gd_client.GetListFeed(sheetKey, worksheetId)
                
        for i, entry in enumerate(feed.entry):
            #each row has at least two key values: shortname, start
            #these will each translate into a StateVariable object
            var = StateVariable()
            var.state = state
            var.value = entry.custom["start"].text
            var.name = entry.custom["shortname"].text
            if (var.name <> None):
                var.save()
                print "%s" % (var)
        
    def processChoices(self, sheetKey, worksheetId, state):
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
            if (choiceno <> None and role <> None):
                c = StateRoleChoice()
                c.state = state
                c.choice = choiceno
                c.desc = entry.custom["desc"].text
                c.role = role
                c.save()
                print '%s' % c
            
    def processTransitions(self, sheetKey, worksheetId, state):  
        feed = self.gd_client.GetListFeed(sheetKey, worksheetId)
        
        for i, entry in enumerate(feed.entry):
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
        if (len(feed.entry) == 3): 
            for i, entry in enumerate(feed.entry):
                id_parts = entry.id.text.split('/')
                worksheetId = id_parts[len(id_parts) - 1]
        
                if (entry.title.text == "Conditions"):
                    self.processConditions(sheetKey, worksheetId, state)
                if (entry.title.text == "Choices"):
                    self.processChoices(sheetKey, worksheetId, state)
                if (entry.title.text == "Transitions"):
                    self.processTransitions(sheetKey, worksheetId, state)  
            
    def processSpreadsheets(self):
        feed = self.gd_client.GetSpreadsheetsFeed()
        for i, entry in enumerate(feed.entry):
            match = re.search("t\d{1}_s\d{1}_*", entry.title.text, re.IGNORECASE)
            if (match):
                
                #parse out a new state object
                state = self.__getOrCreateState(entry.title.text)
                
                # parse out the sheet's identifying key
                id_parts = entry.id.text.split('/')
                key = id_parts[len(id_parts) - 1]   
                              
                #process each of the three expected worksheets
                self.processWorksheets(key, state)
                
    def setupStaticRoles(self):
        president = Role(name="President")
        president.save()
        
        envoy = Role(name="WesternEnvoy")
        envoy.save()
        
        regional = Role(name="SubRegionalRep")
        regional.save()
        
        opposition = Role(name="OppositionLeadership")
        opposition.save()
        
    def t(self):
        self.bulkimport("sdreher.test", "ptero643n")
        
    def bulkimport(self, email, password):
        
        if (email == None or email == ''):
            print "Please enter a valid email address"
            return
        if (password == None or password == ''):
            print "Please enter a valid password"
            return
        
        # initialize the google library stuff
        self.gd_client.email = email
        self.gd_client.password = password
        self.gd_client.ProgrammaticLogin()
        
        #setup static data for roles if they don't already exist
        roles = Role.objects.all()
        if (len(roles) < 1):
            self.setupStaticRoles()
            
        # process the spreadsheets
        self.processSpreadsheets()
        