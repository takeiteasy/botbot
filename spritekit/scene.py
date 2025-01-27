import pygame as pg
import moderngl as mgl
from .base import *
from .parent import *
from .sprite import *

class Scene(Parent):
    def __init__(self):
        super().__init__()
        self.ctx = mgl.get_context()
        info = pg.display.Info()
        self._width = info.current_w
        self._height = info.current_h
        self._projection = glm.ortho(0, self._width, self._height, 0, -1, 1)
        self._view = glm.mat4(1)

    @property
    def projection(self):
        return self._position

    @property
    def view(self):
        return self._view

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def add_child(self, node: BaseNode):
        node.scene = self
        self.children.append(node)

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
