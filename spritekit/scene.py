import pygame as pg
from .sprite import *

class Scene:
    def __init__(self, ctx):
        self.ctx = ctx
        info = pg.display.Info()
        self._width = info.current_w
        self._height = info.current_h
        self._projection = glm.ortho(0, self._width, self._height, 0, -1, 1)
        self.children = []

    @property
    def projection(self):
        return self._position

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def enter(self):
        pass

    def exit(self):
        pass

    def event(self, e):
        pass

    def step(self, delta):
        pass

    def draw(self):
        for child in self.children:
            child.draw()

    def add_child(self, node: BaseNode):
        self.children.append(node)

    def add_children(self, nodes: [BaseNode]):
        self.children.extend(nodes)

    def get_children(self, name: str = ""):
        return [x for x in self.children if x.name == name]

    def rem_children(self, name: str = ""):
        self.children = [x for x in self.children if x.name != name]
