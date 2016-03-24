#Python2 and Python 3 compatibility:
from __future__ import absolute_import, division, print_function, unicode_literals

from six import PY3

class UnicodeMixin(object):
    if PY3:
        __str__ = lambda x: x.__unicode__()
    else:
        __str__ = lambda x: unicode(x).encode('utf-8')

    __repr__ = __str__
