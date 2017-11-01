from __future__ import absolute_import

import base


class DB(base.Base):
    span_type = "db"
    class_name = 'db'

    def __init__(self, project, service, level, trace_id, parent_id):
        super(DB, self).__init__(project, service, self.span_type,
                                     self.class_name, level, trace_id, parent_id)
