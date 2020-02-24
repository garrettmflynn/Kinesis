# -*- coding:utf-8 -*-
'''
:mod:'mneme.core' provides classes for storing memories

Classes from :mod:'mneme.core' return nested data structures containing one or more classes from this module.

Classes:

.. autoclass:: Trace

.. autoclass:: Events
'''
import mneme
from mneme.core.trace import Trace
from mneme.utils.filters import *
from mneme.utils.realtime_streams import *
from mneme.utils.realtime_viewer import *



objectlist = [Trace]

objectnames = [ob.__name__ for ob in objectlist]
class_by_name = dict(zip(objectnames,objectlist))