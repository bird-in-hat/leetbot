''' Merges settings from different locations: (base.py + local.py + env variables). '''

import os
from .base import *


# import settings from a local.py file
try:
    from .local import *
except ImportError:
    raise FileNotFoundError("Did you rename settings/local.py.template as settings/local.py?")
