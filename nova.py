from __future__ import absolute_import

import base


class nova(base.Base):
    span_type = "nova_image"
    class_name = 'nova_image'

    def __init__(self, project, service, level, trace_id, parent_id, starttime, duration):
        super(nova, self).__init__(project, service, self.span_type,
                                   self.class_name, level, trace_id, parent_id, starttime, duration)
