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
    def stringtype(self):
        return self._stringtype

    @property
    def version(self):
        return "{}.{}".format(self._major, self._minor)

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor
