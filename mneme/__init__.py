# -*- coding:utf-8 -*-
'''
Mneme is a package for designing replacement parts for the brain.
'''

import logging
logging_handler = logging.StreamHandler()

from mneme.core import *
from mneme.decode import *
from mneme.utils import *

from mneme.version import version as __version__