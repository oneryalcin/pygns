# -*- coding: utf-8 -*-


class GNSBaseError(Exception):
    """Base exception class for this module"""

    def __init__(self, msg, cause=None):
        super(Error, self).__init__(msg)
        self._cause = cause

    @property
    def cause(self):
        """The underlying exception causing the error, if any."""
        return self._cause


class GNS3GenericError(GNSBaseError):
    """ 
        Users are not supposed to see this error. If they see, then they should report back to developers
    """
    pass


class GNS3ProjectExitsError(GNSBaseError):
    pass


class GNS3ServerConnectionError(GNSBaseError):
    pass
