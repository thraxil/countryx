from django.test import TestCase, RequestFactory, Client
from django.urls import reverse

from .factories import UserFactory, RoleFactory, StateFactory
from countryx.sim.models import Section
from countryx.sim.views import (
    root, allpaths, allquestions, allvariables, CreateSectionView,
    CreateRoleView, StateCreate,
)


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

    def test_allpaths_one_state(self):
        StateFactory()
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
        c.get("/smoketest/")


class CreateSectionViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.v = CreateSectionView.as_view()

    def test_create_no_roles(self):
        u = UserFactory(is_staff=True)
        request = self.factory.post(
            reverse("create-section"),
            dict(
                section_name="test section"
            )
        )
        request.user = u
        response = self.v(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Section.objects.count(), 1)

    def test_create_roles(self):
        u = UserFactory(is_staff=True)
        r = RoleFactory()
        request = self.factory.post(
            reverse("create-section"),
            {
                'section_name': "test section",
                'group_name_0': "test group",
                "group_0_username_%d" % r.id: "foo",
                "group_0_password_%d" % r.id: "bar",
            }
        )
        request.user = u
        response = self.v(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Section.objects.count(), 1)

    def test_create_with_duplicate_username(self):
        u = UserFactory(is_staff=True)
        r = RoleFactory()
        UserFactory(username="foo")
        request = self.factory.post(
            reverse("create-section"),
            {
                'section_name': "test section",
                'group_name_0': "test group",
                "group_0_username_%d" % r.id: "foo",
                "group_0_password_%d" % r.id: "bar",
            }
        )
        request.user = u
        response = self.v(request)
        self.assertEqual(response.status_code, 302)


class CreateRoleViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.v = CreateRoleView.as_view()

    def test_post(self):
        u = UserFactory(is_staff=True)
        request = self.factory.post(
            reverse("create-role"),
            {
                'name': "foo",
                'description': "bar",
            }
        )
        request.user = u
        response = self.v(request)
        self.assertEqual(response.status_code, 302)


class StateCreateTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.v = StateCreate.as_view()

    def test_post(self):
        u = UserFactory(is_staff=True)
        request = self.factory.post(
            reverse("create-state"),
            {
                'turn': 1,
                'state_no': 1,
                'name': "test",
                "description": "some description"
            }
        )
        request.user = u
        response = self.v(request)
        self.assertEqual(response.status_code, 302)
