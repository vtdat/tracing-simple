from __future__ import absolute_import

import base


class vif(base.Base):
    span_type = "vif_driver"
    class_name = 'vif_driver'

    def __init__(self, project, service, level, trace_id, parent_id, starttime, duration):
        super(vif, self).__init__(project, service, self.span_type,
                                   self.class_name, level, trace_id, parent_id, starttime, duration)
