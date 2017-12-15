from __future__ import absolute_import

import base


class stack(base.Base):
    span_type = "stack"
    class_name = 'stack'

    def __init__(self, project, service, level, trace_id, parent_id):
        super(stack, self).__init__(project, service, self.span_type,
                                   self.class_name, level, trace_id, parent_id)
