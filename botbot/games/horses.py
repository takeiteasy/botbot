from ..scene import Scene
from ..raylib import Texture
from ..actor import *
from ..easing import * 
from slimrr import Vector2
import pyray as r
from enum import Enum
import platform
from math import sin
import numpy as np
import random
from typing import Optional

_HORSE_SIZE = (64, 48)
_HORSE_ANIMATIONS = [
    ("Idle", 3, .075),
    ("Eating", 3, .25),
    ("Walking", 8, .5),
    ("Galloping", 6, .075),
    ("Rearing", 8, .5),
    ("Death", 6, .5)
]
_HORSE_COUNT = 8

class HorseOrientation(Enum):
    EAST = 0
    WEST = 1
    SOUTH = 2
    NORTH = 3

def screen_size() -> tuple[Vector2, Vector2]:
    screen = Vector2([r.get_render_width(), r.get_render_height()])
    if platform.system() == "Darwin":
        screen = screen / 2
    return screen, screen / 2.

def _horse_animation(name: str, orientation: HorseOrientation = HorseOrientation.EAST) -> int:
    for i, (n, f, s) in enumerate(_HORSE_ANIMATIONS):
        if n == name:
            return i * (_HORSE_SIZE[1] * 4) + ((orientation.value + 1) * _HORSE_SIZE[1]), f, s
    raise ValueError(f"Animation `{name}` not found")

def _poisson_disc_sampling(width, height, r, k=30):
    cell_size = r / sqrt(2)
    grid_width = int(width / cell_size) + 1
    grid_height = int(height / cell_size) + 1
    grid = [None] * (grid_width * grid_height)
    points = []
    active = []
    first_point = (random.uniform(0, width), random.uniform(0, height))
    points.append(first_point)
    active.append(first_point)
    grid_x, grid_y = int(first_point[0] / cell_size), int(first_point[1] / cell_size)
    grid[grid_y * grid_width + grid_x] = first_point
    while active:
        point_index = random.randint(0, len(active) - 1)
        point = active[point_index]
        found = False
        for _ in range(k):
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(r, 2 * r)
            new_point = (
                point[0] + distance * np.cos(angle),
                point[1] + distance * np.sin(angle))
            if not (0 <= new_point[0] < width and 0 <= new_point[1] < height):
                continue
            grid_x, grid_y = int(new_point[0] / cell_size), int(new_point[1] / cell_size)
            valid = True
            for i in range(max(0, grid_x - 2), min(grid_width, grid_x + 3)):
                for j in range(max(0, grid_y - 2), min(grid_height, grid_y + 3)):
                    neighbor = grid[j * grid_width + i]
                    if neighbor:
                        distance = sqrt((new_point[0] - neighbor[0])**2 + (new_point[1] - neighbor[1])**2)
                        if distance < r:
                            valid = False
                            break
                if not valid:
                    break
            if valid:
                points.append(new_point)
                active.append(new_point)
                grid[grid_y * grid_width + grid_x] = new_point
                found = True
                break
        if not found:
            active.pop(point_index)
    return points

class HorsePen(Actor):
    def __init__(self, number: int, **kwargs):
        super().__init__(**kwargs)
        screen, hscreen = screen_size()
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
        screen, hscreen = screen_size()
        hh = screen.y / _HORSE_COUNT
        py = -hscreen.y + (hh * number + 1) - (_HORSE_SIZE[1] / 4)
        px = -hscreen.x - (_HORSE_SIZE[0] / 2)
        super().__init__(texture=Texture(f"assets/horses/{self._breed}.png"),
                         source=r.Rectangle(0, 0, _HORSE_SIZE[0], _HORSE_SIZE[1]),
                         dst=r.Rectangle(px, py, _HORSE_SIZE[0], _HORSE_SIZE[1]),
                         **kwargs)
        # self._animation =  "Idle" if random() < .5 else "Eating"
        self._animation = "Galloping"
        y, f, s = _horse_animation(self._animation)
        self._animation_y = y
        self._orientation = HorseOrientation.EAST
        self._frame_max = f
        self._frame_current = 0
        self._base_animation_speed = s  # Store the base animation speed
        self._animation_speed = s
        self._timer = TimerNode(duration=s,
                                on_complete=self._on_complete,
                                repeat=True)
        self._target = hscreen.x - _HORSE_SIZE[0]
        self._base_speed = random.uniform(100, 120)
        self._current_speed = self._base_speed
        self._acceleration = 0
        self._time = 0
        self._last_burst = 0
        self._bursts_remaining = 6
        self.add_child(self._timer)

    def _offset(self):
        return self.position + self.origin * (Vector2(list(_HORSE_SIZE)) / 2.)

    def _on_complete(self):
        if self._frame_current + 1 < self._frame_max:
            self._frame_current += 1
        else:
            self._frame_current = 0
    
    def step(self, delta):
        super().step(delta)
        self._time += delta
        # Random chance for speed burst
        if self._bursts_remaining > 0:
            if self._time - self._last_burst > 1.0 and random.random() < 0.025:
                self._acceleration = random.uniform(150, 250)
                self._last_burst = self._time
                self._bursts_remaining -= 1
        # Apply acceleration and decay
        if self._acceleration > 0:
            self._acceleration *= 0.95
        # Natural speed variations
        speed_variation = (
            sin(self._time * 1.5) * 20 +
            sin(self._time * 4.0) * 10
        )
        # Calculate final speed
        self._current_speed = (
            self._base_speed + 
            speed_variation + 
            self._acceleration
        )        
        # Only move if we haven't reached the target
        if self.dst.x < self._target:
            self.dst.x += self._current_speed * delta

    def draw(self):
        r.draw_texture_pro(self.texture,
                           [self._frame_current * _HORSE_SIZE[0], self._animation_y, self.source.width, self.source.height],
                           [self.dst.x, self.dst.y, self.dst.width, self.dst.height],
                           [*-self._offset()], self.rotation, self.color)

class GrassNode(SpriteNode):
    width = 16
    height = 16
    rows = 3
    columns = 3

    def __init__(self, position: Vector2, gtype: Optional[int] = None, **kwargs):
        if gtype is None:
            gtype = random.randint(0, self.__class__.columns * self.__class__.rows - 1)
        row = gtype // self.__class__.columns
        column = gtype % self.__class__.columns
        super().__init__(texture=Texture("assets/Grass.png"),
                         source=r.Rectangle(column * self.__class__.width, row * self.__class__.height, self.__class__.width, self.__class__.height),
                         dst=r.Rectangle(position.x, position.y, self.__class__.width, self.__class__.height),
                         **kwargs)

class HorseRaces(Scene):
    background_color = (129, 186, 68, 255)

    def enter(self):
        screen, hscreen = screen_size()
        points = _poisson_disc_sampling(screen.x, screen.y, 50)
        for p in points:
            self.add_child(GrassNode(Vector2([p[0], p[1]]) - hscreen))
        for i, breed in enumerate(random.sample(list(range(1, _HORSE_COUNT + 1)), _HORSE_COUNT)):
            self.add_child(HorsePen(i + 1))
            name = f"Horse{i + 1}"
            self.add_child(HorseNode(breed, i, name=name))