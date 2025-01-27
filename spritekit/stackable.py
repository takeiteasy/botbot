from .base import *

class Stackable:
    def __init__(self):
        self.children = []

    def add_child(self, node: BaseNode):
        self.children.append(node)

    def add_children(self, nodes: [BaseNode]):
        self.children.extend(nodes)

    def get_children(self, name: str = ""):
        return [x for x in self.children if x.name == name]

    def rem_children(self, name: str = ""):
        self.children = [x for x in self.children if x.name != name]

    def clear_children(self):
        self.children = []
