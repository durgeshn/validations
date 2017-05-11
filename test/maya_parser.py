import os

from maya_scenefile_parser import MayaAsciiParser, MayaBinaryParser
path = r'T:\amol\from_Durgesh\BDG105_004_lay.ma'
nodes = dict()

ext = os.path.splitext(path)[1]
try:
    Base, mode = {
        ".ma": (MayaAsciiParser, "r"),
        ".mb": (MayaBinaryParser, "rb"),
    }[ext]
except KeyError:
    raise RuntimeError("Invalid maya file: %s" % path)


class Parser(Base):
    def on_create_node(self, nodetype, name, parent):
        self.current_node = (name, parent, nodetype)

    def on_set_attr(self, name, value, type):
        if name not in ("nts", "notes"):
            return

        if self.current_node not in nodes:
            nodes[self.current_node] = {}

        nodes[self.current_node][name] = value

        print("{name} = {value} ({type})".format(**locals()))

with open(path, mode) as f:
    parser = Parser(f)
    parser.parse()

import pprint
pprint.pprint(nodes)

# for node, attrs in nodes.iteritems():
#     for key, value in attrs.iteritems():
#         print("{node}.{key} = {value}".format(**locals()))