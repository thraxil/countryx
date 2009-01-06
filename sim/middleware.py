from genocideprevention.sim.models import *
import random, threading

class GameStateMiddleware(object):
    """
    """
    
    __shared_state = dict(write_lock = threading.RLock())

    def __init__(self):
        self.__dict__ = self.__shared_state
                
    def process_request(self, request):
      self.write_lock.acquire()
      try:
         print "GameStateMiddleware: process_request"
         sections = Section.objects.all()
         for section in sections:
            section_turn = section.current_turn()
            
            # verify each group's current state == the current section turn
            # if not, then add the state to the group and make sure all members get automated answers.
            groups = section.sectiongroup_set.all()
            for group in groups:
                group_state = group.sectiongroupstate_set.latest().state
                if (section_turn != group_state.turn):
                
                    group.force_response_all_players()
                   
                    # update the group state to the next turn based on the player choices
                    group.update_state()
                    
      finally:
         self.write_lock.release()
      
      return None