from __future__ import absolute_import

import base


class WSGI(base.Base):
    span_type = "wsgi"
    class_name = 'wsgi'

    def __init__(self, project, service, level, trace_id, parent_id, starttime, duration):
        super(WSGI, self).__init__(project, service, self.span_type,
                                   self.class_name, level, trace_id, parent_id, starttime, duration)
