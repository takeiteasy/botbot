# spritekit/scene.py
#
# Copyright (C) 2025 George Watson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from .actor import ActorType, ActorParent
from .fsm import FiniteStateMachine
import pyray as r
from typing import override
import atexit

__all__ = ["Scene", "main_scene"]

__scene__ = []
__next_scene = None
__drop_scene = None

class Scene(FiniteStateMachine, ActorParent):
    config: dict = {}

    def __init__(self, **kwargs):
        FiniteStateMachine.__init__(self, **kwargs)
        self.camera = r.Camera2D()
        self.camera.target = 0, 0
        self.camera.offset = r.Vector2(r.get_screen_width() / 2, r.get_screen_height() / 2)
        self.camera.zoom = 1.
        self.clear_color = r.RAYWHITE
        self.run_in_background = False
        self.assets = {} # TODO: Store and restore assets to __cache in raylib.py

    @override
    def add_child(self, node: ActorType):
        if node:
            node.__dict__["scene"] = self
            self._add_child(node)
        else:
            raise RuntimeError("Invalid Node")

    def enter(self):
        pass

    def reenter(self):
        pass

    def background(self):
        pass

    def exit(self):
        pass

    def step(self, delta):
        for child in reversed(self.all_children()):
            child.step(delta)

    def step_background(self, delta):
        if self.run_in_background:
            self.step(delta)

    def draw(self):
        r.clear_background(self.clear_color)
        r.begin_mode_2d(self.camera)
        for child in reversed(self.all_children()):
            child.draw()
        r.end_mode_2d()

    def draw_background(self):
        if self.run_in_background:
            self.draw()

    @classmethod
    def push_scene(cls, scene):
        if not isinstance(scene, Scene):
            raise RuntimeError("Invalid Scene")
        global __next_scene
        if __next_scene is not None:
            raise RuntimeError("Next scene already queued")
        __next_scene = scene

    @classmethod
    def drop_scene(cls):
        global __scene__, __drop_scene
        if __drop_scene is not None:
            raise RuntimeError("Drop scene already queued")
        __drop_scene = __scene__[-1:]

    @classmethod
    def first_scene(cls):
        global __scene__, __drop_scene
        __drop_scene = __scene__[1:]

    @classmethod
    def current_scene(cls):
        if not __scene__:
            raise RuntimeError("No active Scene")
        return __scene__[-1]

    @classmethod
    def main_scene(cls):
        global __next_scene
        if __next_scene is None:
            raise RuntimeError("No next scene queued")
        return __scene__[0]
    
    @property
    def width(self):
        return r.get_screen_width()
    
    @property
    def height(self):
        return r.get_screen_height()
