class Base(object):

    def __init__(self, project=None, service=None,
                 span_type=None, class_name=None, level = None, trace_id = None, parent_id = None):
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.project = project
        self.service = service
        self.span_type = span_type
        self.class_name = class_name
        self.level = level
        self.signature = []   # This actually is a posting list (str type)
        self.nodes = []         # A list contains all node in workflow

    def construct(self, data):
        pass

    def append(self, node):
        self.nodes.append(node)

    def create_signature(self, nodes):
        if not nodes:
            return 
        for node in nodes:
            self.signature.append(node.class_name + str(node.level))
            self.create_signature(node.nodes)