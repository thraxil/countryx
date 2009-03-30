from django.core.management.base import BaseCommand, CommandError
from django.core import serializers
from optparse import make_option
from countryx.sim.models import *
import csv, time, datetime


class Command(BaseCommand):
    def handle(self, *app_labels, **options):
        args = 'Usage: python manage.py import_users --csv csv file'
        if not options.get('csv'):
            print args
            return
            
        fh = open(options.get('csv'), 'r')
        table = csv.reader(fh)
        self.process_rows(list(table))

    def process_rows(self,rows):
        for row in rows:
            (last,first,uni) = row
            self.get_or_create_user(uni,first,last)
	

    def get_or_create_user(self, uni, first, last):
        try:
            user = User.objects.get(username=uni)
        except User.DoesNotExist:
            password='wind user'
            user = User(username=uni,
                        first_name=first,
                        last_name=last,
                        email=uni + "@columbia.edu",
                        is_staff=False,
                        is_superuser=False,
                        is_active=True)
            user.set_password(password)
            user.set_unusable_password()
            user.save()
        return user

    option_list = BaseCommand.option_list + (
        make_option('--csv', dest='csv', help='Base CSV file to import'),
    )

