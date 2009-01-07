from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from optparse import make_option
from genocideprevention.sim.models import *
import csv, time, datetime,sys


class Command(BaseCommand):
    def clean(self):
        print "Deleting from SectionGroupPlayerTurn...."
        SectionGroupPlayerTurn.objects.all().delete()
        
        print "Deleting from SectionGroupState...."
        SectionGroupState.objects.all().delete()

        print "Deleting from SectionGroupPlayer...."
        SectionGroupPlayer.objects.all().delete()
        
        print "Deleting from SectionGroup...."
        SectionGroup.objects.all().delete()
        
        print "Deleting from SectionTurnDates..."
        SectionTurnDates.objects.all().delete()
        
        print "Deleting from SectionGroupState...."
        SectionAdministrator.objects.all().delete()
        
        print "Deleting from Section...."
        Section.objects.all().delete()
                        
    def handle(self, *app_labels, **options):
        # kill everything associated with this section
        
        result = raw_input("Are you sure you want to delete all data related to sections, groups and users? y/n\r\n")
        
        if (result == 'n' or result == 'N'):
            print "Canceling..."
        elif (result == 'y' or result == 'Y'):
          self.clean()
          print "Cleaning complete"  
        else:
            print "Did not understand the command. Quitting."
        