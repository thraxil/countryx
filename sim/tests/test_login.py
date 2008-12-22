from django.test.client import Client
from django.test import TestCase
from genocideprevention.sim.models import *

class LoginTestCases(TestCase):
    fixtures = ["test_data.json"]

    def test_index_not_logged_in(self):
        # Issue a GET request for the index page
        client = Client()
        response = client.get('/sim/')
        
        self.assertRedirects(response, expected_url="/accounts/login/?next=/sim/", status_code=302, target_status_code=200)
                
    def test_django_login(self):
        client = Client()
        
        # Issue a POST request for the login page that has the required username,password supplied
        response = client.post('/accounts/login/', {'username': 'testuser', 'password': 'test', "next": "/sim/"})
        
        self.assertRedirects(response, expected_url="/sim/", status_code=302, target_status_code=200)
        
        # Now that the user is logged in, verify they are sent to the right place
        response = client.get('/sim/')
        self.assertContains(response, "Welcome", status_code=200)
        self.assertTemplateUsed(response, "sim/player_index.html")
        
    def test_django_invalid_password(self):
        client = Client()
                
        # Issue a POST request for the login page that has the required username,password supplied
        response = client.post('/accounts/login/', {'username': 'testuser', 'password': 'foo', "next": "/sim/"})
                 
        self.assertContains(response, "Your username and password didn't match", status_code=200)
        self.assertTemplateUsed(response, "registration/login.html")
        
        self.assertFormError(response, "form", "__all__", "Please enter a correct username and password. Note that both fields are case-sensitive.")
        
    def test_django_already_loggedin(self):
        # Do a fake login via the handy client login fixture
        c = Client()
        uname = u'testuser'
        pwd = u'test'
        self.assert_(c.login(username=uname, password=pwd))
        
        response = c.get('/sim/')
        self.assertContains(response, "Welcome", status_code=200)
        self.assertTemplateUsed(response, "sim/player_index.html")

    def test_django_logout(self):
        # Do a fake login via the handy client login fixture
        c = Client()
        self.assert_(c.login(username=u'testuser', password=u'test'))
        
        response = c.get('/sim/logout/')
        self.assertContains(response, "logged out", status_code=200)   
        self.assertTemplateUsed(response, "sim/logged_out.html")
        
    def test_django_faculty_login(self):
        client = Client()
        
        # Issue a POST request for the login page that has the required username,password supplied
        response = client.post('/accounts/login/', {'username': 'testfaculty', 'password': 'faculty', "next": "/sim/"})
        
        self.assertRedirects(response, expected_url="/sim/", status_code=302, target_status_code=200)
        
        # Now that the user is logged in, verify they are sent to the right place
        response = client.get('/sim/')
        self.assertContains(response, "Welcome", status_code=200)
        self.assertTemplateUsed(response, "sim/faculty_index.html")