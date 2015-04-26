from django.test import TestCase, RequestFactory, Client

from .factories import UserFactory, SectionAdministratorFactory
from countryx.sim.views import root


class RootTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_player(self):
        request = self.factory.get("/")
        request.user = UserFactory()
        response = root(request)
        self.assertEqual(response.status_code, 200)

    def test_faculty(self):
        request = self.factory.get("/")
        request.user = SectionAdministratorFactory().user
        response = root(request)
        self.assertEqual(response.status_code, 200)


class SmoketestTest(TestCase):
    def test_smoketest(self):
        c = Client()
        r = c.get("/smoketest/")
        self.assertEqual(r.status_code, 200)
