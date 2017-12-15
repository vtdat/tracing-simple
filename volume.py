from __future__ import absolute_import

import base


class volume(base.Base):
    span_type = "volume"
    class_name = 'volume'

    def __init__(self, project, service, level, trace_id, parent_id):
        super(volume, self).__init__(project, service, self.span_type,
                                   self.class_name, level, trace_id, parent_id)
