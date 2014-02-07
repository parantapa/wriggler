"""
Wriggler crawler module.
"""

from logbook import Logger
log = Logger(__name__)

class Error(Exception):
    """
    All exceptions returned are subclass of this one.
    """
