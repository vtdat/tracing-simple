from __future__ import absolute_import

import base


class driver(base.Base):
    span_type = "driver"
    class_name = 'driver'

    def __init__(self, project, service, level, trace_id, parent_id):
        super(driver, self).__init__(project, service, self.span_type,
                                   self.class_name, level, trace_id, parent_id)
