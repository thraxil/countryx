from countryx.sim.models import *
import random, threading

class GameStateMiddleware(object):
    """
    """
    
    __shared_state = dict(write_lock = threading.RLock())

    def __init__(self):
        self.__dict__ = self.__shared_state
                
    def process_request(self, request):
        if request.path.startswith("/admin/") \
                or request.path.startswith("/accounts") \
                or request.path.startswith("/site_media") \
                or request.META['SERVER_NAME'] == 'testserver':
            return # skip it in admin otherwise we can't add a section
        self.write_lock.acquire()
        try:
            sections = Section.objects.all()
            for section in sections:
                section_turn = section.current_turn()
                # verify each group's current state == the current section turn
                # if not, then add the state to the group and make sure all members get automated answers.
                groups = section.sectiongroup_set.all()
                for group in groups:
                    try:
                        group_state = group.sectiongroupstate_set.latest().state
                    except SectionGroupState.DoesNotExist:
                        group_state = State.objects.get(state_no=1,turn=1)
                        sgs = SectionGroupState.objects.create(state=group_state,group=group,
                                                               date_updated=datetime.datetime.now())
                    if (section_turn != group_state.turn):
                        group.force_response_all_players()
                        # update the group state to the next turn based on the player choices
                        group.update_state()
        finally:
            self.write_lock.release()
        return None
