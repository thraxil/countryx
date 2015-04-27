from django.test import TestCase, RequestFactory, Client

from .factories import UserFactory
from countryx.sim.views import root, allpaths, allquestions, allvariables


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
        request.user = UserFactory(is_staff=True)
        response = root(request)
        self.assertEqual(response.status_code, 200)


class AllPathsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_allpaths_empty(self):
        request = self.factory.get("/")
        request.user = UserFactory()
        response = allpaths(request)
        self.assertEqual(response.status_code, 200)


class AllQuestionsTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_allquestions_empty(self):
        request = self.factory.get("/")
        request.user = UserFactory()
        response = allquestions(request)
        self.assertEqual(response.status_code, 200)


class AllVariablesTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_allpaths_empty(self):
        request = self.factory.get("/")
        request.user = UserFactory()
        response = allvariables(request)
        self.assertEqual(response.status_code, 200)


class SmoketestTest(TestCase):
    def test_smoketest(self):
        c = Client()
        r = c.get("/smoketest/")
        self.assertEqual(r.status_code, 200)
