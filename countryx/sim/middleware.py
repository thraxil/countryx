from countryx.sim.models import Section
import threading


def ensure_consistency_of_all_sections():
    for section in Section.objects.all():
        section.ensure_consistency()

# Note from AP:
# this middleware needs to go away. We need better test coverage
# before we can do that safely, but
#   1) middleware is just the wrong place to be doing this
#   2) this middleware runs over every single Section in the
#      database on every single request that hits the entire site
#      (minus a few exceptions) even though it's only very
#      infrequently that it actually does something (the first)
#      request that goes through after a turn deadline passes. It
#      appears that this was implemented this way as sort of a
#      poor replacement for a cronjob or background process that
#      would enfore the turn deadlines. I would recommend switching
#      to a Celery periodic task or something similar instead.
#   3) my understanding is that most of the time now, Country X is
#      used in "workshop" mode where the whole thing is run through
#      in a few hours and the instructor just manually advances the
#      turns when the group indicates that they have all finished. The
#      original mode where it ran over a week or so with turns switching
#      automatically at preset points in time is almost never used anymore
#      (and is the driving force for this entire middleware)


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
