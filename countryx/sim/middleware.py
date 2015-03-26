from countryx.sim.models import Section
import threading


def ensure_consistency_of_all_sections():
    for section in Section.objects.all():
        section.ensure_consistency()


class GameStateMiddleware(object):
    __shared_state = dict(write_lock=threading.RLock())

    def __init__(self):
        self.__dict__ = self.__shared_state

    def process_request(self, request):
        if request.path.startswith("/admin/") \
                or request.path.startswith("/accounts") \
                or request.path.startswith("/site_media") \
                or request.META['SERVER_NAME'] == 'testserver':
            return  # skip it in admin otherwise we can't add a section
        self.write_lock.acquire()
        try:
            ensure_consistency_of_all_sections()
        finally:
            self.write_lock.release()
        return None
