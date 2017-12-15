from __future__ import absolute_import

import base


class RPC(base.Base):
    span_type = "rpc"
    class_name = 'rpc'

    def __init__(self, project, service, level, trace_id, parent_id):
        super(RPC, self).__init__(project, service, self.span_type,
                                   self.class_name, level, trace_id, parent_id)
