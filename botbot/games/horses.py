from ..scene import Scene
from ..raylib import Texture, TextureFromImage
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

def _screen_size() -> tuple[Vector2, Vector2]:
    screen = Vector2([r.get_render_width(), r.get_render_height()])
    if platform.system() == "Darwin":
        screen = screen / 2
    return screen, screen / 2.

def _horse_animation(name: str, orientation: HorseOrientation = HorseOrientation.EAST) -> tuple[int, float, float]:
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

class BaseHorseNode(SpriteNode):
    def _offset(self):
        return self.position + self.origin - (Vector2(list(_HORSE_SIZE)) / 2.)

class HorseCustomization(BaseHorseNode):
    def __init__(self, texture: Texture, **kwargs):
        super().__init__(texture=texture, **kwargs)
    
    def step(self, _):
        self.position = self.parent.position
        self.origin = self.parent.origin
        self.source = self.parent.source
        self.dst = self.parent.dst

class HorseNode(BaseHorseNode): 
    def __init__(self, breed: int, number: int, race_name: str, **kwargs):
        self._breed = breed
        self._race_name = race_name
        screen, hscreen = _screen_size()
        hh = (hscreen.y / 2.) / _HORSE_COUNT
        py = (hscreen.y / 4.) + (hh * number + 1) - (_HORSE_SIZE[1] / 4)
        px = -hscreen.x - (_HORSE_SIZE[0] / 2)
        super().__init__(texture=Texture(f"assets/horses/{self._breed}.png"),
                         source=r.Rectangle(0, 0, _HORSE_SIZE[0], _HORSE_SIZE[1]),
                         dst=r.Rectangle(px, py, _HORSE_SIZE[0], _HORSE_SIZE[1]),
                         **kwargs)
        self._animation = "Galloping"
        y, f, s = _horse_animation(self._animation)
        self._animation_y = y
        self._orientation = HorseOrientation.EAST
        self._frame_max = f
        self._frame_current = 0
        self._base_animation_speed = s
        self._animation_speed = s
        self._timer = TimerNode(duration=s,
                                on_complete=self._on_complete,
                                repeat=True)
        self._target = hscreen.x - _HORSE_SIZE[0]
        self._move_target = hscreen.x + _HORSE_SIZE[0]
        self._base_speed = random.uniform(100, 120)
        self._current_speed = self._base_speed
        self._acceleration = 0
        self._time = 0
        self._last_burst = 0
        self._burst_cooldown = random.uniform(.5, 2.)
        self._bursts_remaining = 4
        self._burst_chance = .1
        self._finished = False
        self.add_child(self._timer)
        if random.random() < .5:
            self.add_child(HorseCustomization(texture=Texture(f"assets/horses/customizations/markings/{random.randint(1, 8)}.png")))
        if random.random() < .5:
            self.add_child(HorseCustomization(texture=Texture(f"assets/horses/customizations/hair/{random.randint(1, 30)}.png")))

    def _on_complete(self):
        if self._frame_current + 1 < self._frame_max:
            self._frame_current += 1
        else:
            self._frame_current = 0
    
    @property
    def burst_chance(self):
        return self._burst_chance
    
    @burst_chance.setter
    def burst_chance(self, value):
        self._burst_chance = value
    
    def step(self, delta):
        self._time += delta
        if self._bursts_remaining > 0 and not self._finished:
            if self._time - self._last_burst > self._burst_cooldown and random.random() < self._burst_chance:
                self._acceleration = random.uniform(200., 250.)
                self._last_burst = self._time
                self._bursts_remaining -= 1
                self._burst_cooldown = random.uniform(.5, 2.)
        if self._acceleration > 0:
            self._acceleration *= 0.95
        speed_variation = (sin(self._time * 2.0) * 20 +
                            sin(self._time * 3.0) * 10)
        self._current_speed = (
            self._base_speed + 
            speed_variation + 
            self._acceleration)
        if not self._finished and (self.dst.x + _HORSE_SIZE[0] - 12) >= self._target:
            self._finished = True
        if self.dst.x < self._move_target:
            self.dst.x += self._current_speed * delta
            self.source.x = self._frame_current * _HORSE_SIZE[0]
            self.source.y = self._animation_y
            super().step(delta)
        else:
            self.remove_me()

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

class CheckerboardNode(SpriteNode):
    def __init__(self,
                 position: Vector2,
                 size: Vector2,
                 check_size: Vector2 = Vector2([16, 16]),
                 color1: tuple[int, int, int, int] = (255, 255, 255, 255),
                 color2: tuple[int, int, int, int] = (0, 0, 0, 255),
                 **kwargs):
        image = r.gen_image_checked(int(size.x), int(size.y), int(check_size.x), int(check_size.y), color1, color2)
        super().__init__(texture=TextureFromImage(image),
                         dst=r.Rectangle(position.x, position.y, size.x, size.y),
                         **kwargs)

class FenceNode(Actor):
    def __init__(self, height: int, divisions: int, **kwargs):
        super().__init__(**kwargs)
        screen, hscreen = _screen_size()
        self.add_child(LineNode(position=Vector2([-hscreen.x, 0]),
                                end=Vector2([hscreen.x, 0]),
                                thickness=3,
                                color=(0, 0, 0, 255)))
        self.add_child(LineNode(position=Vector2([-hscreen.x, -height]),
                                end=Vector2([hscreen.x, -height]),
                                thickness=3,
                                color=(0, 0, 0, 255)))
        for i in range(int(hscreen.x) // divisions):
            offset = (i + 1) * (divisions * 2)
            self.add_child(LineNode(position=Vector2([-hscreen.x + offset, 0]),
                                    end=Vector2([-hscreen.x + offset, -height]),
                                    thickness=3,
                                    color=(0, 0, 0, 255)))

class BaseFanNode(SpriteNode):
    counts = {
        "Male": {
            "Body": 3,
            "Shoes": 3,
            "Pants": 3,
            "Mouth": 3,
            "Eyes": 5,
            "Shirt": 7,
            "Hairstyles": 7,
            "Accessories": 7
        },
        "Female": {
            "Body": 3,
            "Shoes": 3,
            "Mouth": 3,
            "Eyes": 3,
            "Shirt": 5,
            "Hairstyles": 5,
            "Accessories": 5
        }
    }
    folder_map = {
        "Body": "00 - Body",
        "Shoes": "01 - Shoes",
        "Pants": "02 - Pants",
        "Mouth": "03 - Mouth",
        "Eyes": "04 - Eyes",
        "Shirt": "05 - Shirts",
        "Hairstyles": "06 - Hairstyles",
        "Accessories": "07 - Accessories"
    }
    file_map = {
        "Body": "Body",
        "Shoes": "Shoes",
        "Pants": "Pants",
        "Mouth": "Mouth",
        "Eyes": "Eye",
        "Shirt": "Shirt",
        "Hairstyles": "Hair",
        "Accessories": "Acc"
    }
    size = (19, 32)

    def _offset(self):
        return self.position + self.origin - (Vector2(list(self.__class__.size)) / 2.)

class FanAccessoryNode(BaseFanNode):
    def __init__(self, gender: str, body_part: str, index: int, **kwargs):
        self.gender = gender
        path = self.__class__.folder_map[body_part]
        file = self.__class__.file_map[body_part]
        if body_part == "Eyes" and self.gender == "Female":
            file = "Eyes"
        super().__init__(texture=Texture(f"assets/people/{self.gender}/{path}/{file}0{index}.png"),
                         **kwargs)

    def step(self, delta):
        self.position = self.parent.position
        self.origin = self.parent.origin
        self.source = self.parent.source
        self.dst = self.parent.dst

class FanNode(BaseFanNode):
    def __init__(self, position: Vector2, **kwargs):
        self.gender = random.choice(["Male", "Female"])
        self.accessories = { k: random.randint(1, v) for k, v in self.__class__.counts[self.gender].items() }
        self.body = self.accessories.pop("Body")
        super().__init__(texture=Texture(f"assets/people/{self.gender}/00 - Body/Body0{self.body}.png"),
                         source=r.Rectangle(0, 0, self.__class__.size[0], self.__class__.size[1]),
                         dst=r.Rectangle(position.x, position.y, self.__class__.size[0], self.__class__.size[1]),
                         **kwargs)
        for k, v in self.accessories.items():
            if self.gender == "Female" and k == "Pants":
                continue
            self.add_child(FanAccessoryNode(self.gender, k, v))

class StandsNode(Actor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        screen, hscreen = _screen_size()
        center = Vector2([hscreen.x / 2., -hscreen.y / 2.])
        inner_box = hscreen - 50
        self.add_child(RectangleNode(position=center,
                                     width=hscreen.x,
                                     height=hscreen.y,
                                     color=r.GRAY))
        self.add_child(RectangleNode(position=center,
                                     width=inner_box.x,
                                     height=inner_box.y,
                                     color=(100, 100, 100, 255)))
        points = [(p[0] + FanNode.size[0], p[1] + FanNode.size[1]) for p in _poisson_disc_sampling(inner_box.x - 50, inner_box.y - 50, 60)]
        for p in [Vector2([p[0] + 25, p[1] + 25 - hscreen.y])for p in points]:
            self.add_child(FanNode(position=p))
        self.add_child(FenceNode(height=20, divisions=20))

class HorseRaces(Scene):
    background_color = (129, 186, 68, 255)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._horse_names = open("assets/names.txt", "r").read().split("\n")
    
    def add_horses(self):
        for i in range(_HORSE_COUNT):
            self.remove_children(name=f"Horse{i + 1}")
        names = random.sample(self._horse_names, _HORSE_COUNT)
        for i, breed in enumerate(random.sample(list(range(1, _HORSE_COUNT + 1)), _HORSE_COUNT)):
            self.add_child(HorseNode(breed, i, race_name=names[i], name=f"Horse{i + 1}"))

    def enter(self):
        screen, hscreen = _screen_size()
        for p in _poisson_disc_sampling(screen.x, screen.y, 50):
            self.add_child(GrassNode(Vector2([p[0], p[1]]) - hscreen))
        self._target = hscreen.x - _HORSE_SIZE[0]
        self.add_child(StandsNode())
        self.add_child(CheckerboardNode(position=Vector2([self._target + (_HORSE_SIZE[0] / 2.),
                                                          hscreen.y / 2.]),
                                        size=Vector2([_HORSE_SIZE[0], hscreen.y])))
        self.add_child(LineNode(position=Vector2([self._target, 0]),
                                end=Vector2([self._target, screen.y]),
                                thickness=3,
                                color=(255, 0, 0, 255)))   
        self.add_horses()
    
    def step(self, delta):
        remaining_horses = [x for x in [self.find_child(name=f"Horse{i + 1}") for i in range(_HORSE_COUNT)] if x is not None]
        for i, horse in enumerate(sorted(remaining_horses, key=lambda x: x.dst.x)):
            horse.burst_chance = .1 + (i * .1)
        super().step(delta)