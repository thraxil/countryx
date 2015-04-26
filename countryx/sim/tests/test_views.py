from django.test import TestCase, RequestFactory

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
