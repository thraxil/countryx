from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
     
def root(request):
    return HttpResponseRedirect("/sim/")

