from django.test.client import Client
from django.test import TestCase
from genocideprevention.sim.models import *
from django.utils.translation import ugettext_lazy as _

class ViewTestCase(TestCase):
    fixtures = ['testdata']
    
    def test_fixture(self):
        role = Role.objects.get(name="President")
        self.assert_(role)

#    def test_index_not_logged_in(self):
#        # Issue a GET request for the index page
#        client = Client()
#        response = client.get('/sim/')
#        
#        # Check that the response is 200 OK and that we're on the login page
#        self.assertContains(response, "login", status_code=200)
#
#        # Check that the context is what we expect
#        self.failUnlessEqual(len(response.context[0]["error_message"]), 0)
#        self.assertTemplateUsed(response, "sim/login.html")

#    def test_django_login_no_cookies(self):
#        #The test fixture does not support the test cookie setting.
#        #exploiting this to test the "no cookies" path
#                
#        # Issue a POST request for the login page that has the required username,password supplied
#        response = self.client.post('/sim/login/', {'username': 'testuser', 'password': 'test'})
#        
#        # Check that the response is 200 OK and that we're on the login page
#        self.assertContains(response, "login", status_code=200)
#        self.assert_(response.context[0]["error_message"].find("enable cookies") > 0)
#        
#    def test_django_login(self):
#        # Do a fake login via the handy client login fixture
#        c = Client()
#        uname = u'testuser'
#        pwd = u'test'
#        self.assert_(c.login(username=uname, password=pwd))
#        
#        response = c.get('/sim/')
#        
#        # Check that the response is 200 OK and that we're on the login page
#        print response.content
#        self.assertContains(response, "Welcome", status_code=200)
#
#        # Check that the context is what we expect
#        self.failUnlessEqual(len(response.context[0]["error_message"]), 0)
#        self.assertTemplateUsed(response, "sim/index.html")
        

  
        
        
        