import sys


class VersionHelpers(object):
    def __init__(self):
        self._major = sys.version_info[0]
        self._minor = sys.version_info[1]
        if self._major < 3:
            # Set Python 2.x specifics
            self._stringtype = basestring
        else:
            # Set Python 3.x + specifics
            self._stringtype = str

    @property
    def STRINGTYPE(self):
        return self._stringtype

    @property
    def VERSION(self):
        return "{}.{}".format(self._major, self._minor)

    @property
    def MAJOR(self):
        return self._major

    @property
    def MINOR(self):
        return self._minor
