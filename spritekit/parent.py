from .base import *
from typing import Optional

class Parent:
    def __init__(self):
        self.children = []

    def add_child(self, node: BaseNode):
        self.children.append(node)

    def add_children(self, nodes: [BaseNode]):
        for node in nodes:
            self.add_child(node)

    def get_children(self, name: Optional[str] = ""):
        return [x for x in self.children if x.name == name]

    def rem_children(self, name: Optional[str] = ""):
        self.children = [x for x in self.children if x.name != name]

    def clear_children(self):
        self.children = []
