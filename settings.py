from settings_shared import *

DATABASE_USER='postgres'
DATABASE_PASSWORD='postgres'

try:
    from local_settings import *
except ImportError:
    pass
