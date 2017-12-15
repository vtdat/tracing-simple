from __future__ import absolute_import

import base


class compute(base.Base):
    span_type = "compute"
    class_name = 'compute'

    def __init__(self, project, service, level, trace_id, parent_id):
        super(compute, self).__init__(project, service, self.span_type,
                                   self.class_name, level, trace_id, parent_id)
