from __future__ import absolute_import

import base


class neutron(base.Base):
    span_type = "neutron"
    class_name = 'neutron'

    def __init__(self, project, service, level, trace_id, parent_id):
        super(neutron, self).__init__(project, service, self.span_type,
                                   self.class_name, level, trace_id, parent_id)
