from smoketest import SmokeTest
from models import State


class DBConnectivity(SmokeTest):
    def test_retrieve(self):
        cnt = State.objects.all().count()
        self.assertTrue(cnt > 0)
