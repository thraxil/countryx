from genocideprevention.sim.models import *

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
            turn_dates = SectionTurnDates.object.get(section=section)
            
            # verify each group's current state == the current section turn
                      
            
            
         
      finally:
         self.write_lock.release()
      
      return None