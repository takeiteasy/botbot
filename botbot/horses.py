from .scene import Scene
from .raylib import Texture
from .actor import Actor, RectangleNode, CircleNode, LabelNode, LineNode, SpriteNode, TimerNode
from slimrr import Vector2
import pyray as r
from dataclasses import dataclass
from typing import Optional
from random import randint, random, sample
from enum import Enum
import platform

_HORSE_SIZE = (64, 48)
_HORSE_ANIMATIONS = [
    ("Idle", 3, .075),
    ("Eating", 3, .25),
    ("Walking", 8, .5),
    ("Galloping", 6, .5),
    ("Rearing", 8, .5),
    ("Death", 6, .5)
]
_HORSE_COUNT = 8

class HorseOrientation(Enum):
    EAST = 0
    WEST = 1
    SOUTH = 2
    NORTH = 3

def _horse_animation(name: str, orientation: HorseOrientation = HorseOrientation.EAST) -> int:
    for i, (n, f, s) in enumerate(_HORSE_ANIMATIONS):
        if n == name:
            return i * (_HORSE_SIZE[1] * 4) + ((orientation.value + 1) * _HORSE_SIZE[1]), f, s
    raise ValueError(f"Animation `{name}` not found")

class HorsePen(Actor):
    def __init__(self, number: int, **kwargs):
        super().__init__(**kwargs)
        screen = Vector2([r.get_render_width(), r.get_render_height()])
        if platform.system() == "Darwin":
            screen = screen / 2
        hscreen = screen / 2.
        size = 90.
        hsize = size / 2.
        hh = screen.y / _HORSE_COUNT
        center = Vector2([-hscreen.x + hsize,
                          -hscreen.y + (hh * number + 1) - (_HORSE_SIZE[1] / 4) - hsize])
        self.add_child(RectangleNode(color=r.RED,
                                     position=center ,
                                     width=size,
                                     height=size))
        self.add_child(CircleNode(color=r.WHITE,
                                  position=center,
                                  radius=hsize - 10))
        self.add_child(LabelNode(text=f"{number}",
                                 position=center,
                                 font_size=72,
                                 color=r.BLACK))
        self.add_child(LineNode(color=r.WHITE,
                                thickness=12.,
                                position=center + Vector2([-hsize, hsize]),
                                end=center + Vector2([screen.x, hsize])))

class HorseNode(SpriteNode): 
    def __init__(self, breed: int, number: int, **kwargs):
        self._breed = breed
        rh = r.get_render_height()
        rw = r.get_render_width()
        if platform.system() == "Darwin":
            rh = rh / 2
            rw = rw / 2
        hh = rh / _HORSE_COUNT
        py = -(rh / 2) + (hh * number + 1) - (_HORSE_SIZE[1] / 4)
        px = -(rw / 2) - (_HORSE_SIZE[0] / 2)
        super().__init__(texture=Texture(f"assets/horses/{self._breed}.png"),
                         source=r.Rectangle(0, 0, _HORSE_SIZE[0], _HORSE_SIZE[1]),
                         dst=r.Rectangle(px, py, _HORSE_SIZE[0], _HORSE_SIZE[1]),
                         **kwargs)
        self._animation =  "Idle" if random() < .5 else "Eating"
        y, f, s = _horse_animation(self._animation)
        self._animation_y = y
        self._orientation = HorseOrientation.EAST
        self._frame_max = f
        self._frame_current = 0
        self._speed = s
        self._timer = TimerNode(duration=s,
                                on_complete=self._on_complete,
                                repeat=True)
        self.add_child(self._timer)

    def _offset(self):
        return self.position + self.origin * (Vector2(list(_HORSE_SIZE)) / 2.)

    def _on_complete(self):
        if self._frame_current + 1 < self._frame_max:
            self._frame_current += 1
        else:
            self._frame_current = 0

    def draw(self):
        r.draw_texture_pro(self.texture,
                           [self._frame_current * _HORSE_SIZE[0], self._animation_y, self.source.width, self.source.height],
                           [self.dst.x, self.dst.y, self.dst.width, self.dst.height],
                           [*-self._offset()], self.rotation, self.color)
    
class HorseRaces(Scene):
    background_color = (129, 186, 68, 255)

    def enter(self):
        for i, breed in enumerate(sample(list(range(1, _HORSE_COUNT + 1)), _HORSE_COUNT)):
            self.add_child(HorsePen(i + 1))
            self.add_child(HorseNode(breed, i))