from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from optparse import make_option
from genocideprevention.sim.models import *
import csv

class Command(BaseCommand):
	IDX_USERNAME = 0
	IDX_ROLE = 1
	IDX_GAME_GROUP = 2
	IDX_GAME_ROLE = 3
	
	def get_or_create_group(self, groupname, section):
		try:
			group = SectionGroup.objects.get(name=groupname, section=section)
		except SectionGroup.DoesNotExist:
			group = SectionGroup.objects.create(name=groupname, section=section)
			start_state = State.objects.get(turn=1, state=1)
			SectionGroupState.objects.create(group=group, state=start_state)
			
		return group
		
	def get_game_role(self, roleName):
		try:
			role = Role.objects.get(name=roleName)
		except Role.DoesNotExist:
			role = None
		return role
	
	def get_or_create_section(self, sectionName, term, year):
		try:
			section = Section.objects.get(name=sectionName, term=term, year=year)
		except Section.DoesNotExist:
			section = Section.objects.create(name=sectionName, term=term, year=year, created_date=datetime.datetime.now())
		return section
	
	def get_or_create_user(self, username):
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			user = User(username=username, password='wind user')
			user.set_unusable_password()
			user.save()
		return user
    

	def process_rows(self, rows, section):
		print "process_rows"
		for row in rows:
			username = row[self.IDX_USERNAME]
			user = self.get_or_create_user(username)
        	
			role = row[self.IDX_ROLE]
			if (role == 'Administrator'):
				user.is_staff = True
				user.save()
				SectionAdministrator.objects.create(user=user, section=section)
			elif (role == 'Student'):
				game_group = self.get_or_create_group(row[self.IDX_GAME_GROUP], section)
				game_role = self.get_game_role(row[self.IDX_GAME_ROLE])
        		
				# verify a role matching this name exists
				if (game_role is None):
					print "Invalid game role specified [%s]" % (row[self.IDX_GAME_ROLE])
					return
        		
				# Verify there's no player in this role already.
				qs = SectionGroupPlayer.objects.filter(group=game_group, role=game_role)
				if (len(qs) > 0):
					player = list(qs)[0]
					if (player.user != user):
						print "Cannot add [%s] to [%s] group as [%s] role: Player already exists for that role [%s]" % (user, game_group, game_role, player)
						return
				SectionGroupPlayer.objects.create(user=user, group=game_group, role=game_role)

	option_list = BaseCommand.option_list + (
        make_option('--csv', dest='csv', help='Base CSV file to import'),
        make_option('--section', dest='section', help='Short descriptive class name'),
        make_option('--term', dest='term', help='Valid values: Spring, Summer, Fall'),
        make_option('--year', dest='year', help='Year the class is taking place'),
        make_option('--clean', dest='clean', help='Whether the player tables for this section should be cleaned before continuing', action='store_const', const=True),
    )
	            
	def handle(self, *app_labels, **options):
		args = 'Usage: python manage.py import_groups --csv csv file --section --term --year [--clean]'
		
		#if (options.get('clean')):
			# kill everything associated with this section
					
		if not options.get('csv') or not options.get('section') or not options.get('term') or not options.get('year'):
			print args
			return
            
		section = options.get('section')
		term = options.get('term')
		year = options.get('year')
        
		section = self.get_or_create_section(section, term, year)
        
		fh = open(options.get('csv'), 'r')
		table = csv.reader(fh)
		self.process_rows(list(table), section)
	        	
		    
