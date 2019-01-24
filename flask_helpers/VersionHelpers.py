import sys


class VersionHelpers(object):
    def __init__(self):
        self.major = sys.version_info[0]
        if self.major < 3:
            # Set Python 2.x specifics
            self.STRINGTYPE = basestring
        else:
            # Set Python 3.x + specifics
            self.STRINGTYPE = str
