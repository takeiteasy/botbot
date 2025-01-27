from .base import *
from .stackable import *
import glm

class Node(BaseNode, Stackable):
    def __init__(self,
                 name: str = "",
                 position: glm.vec2 = glm.vec2(0, 0),
                 z: float = 0,
                 rotation: float = 0,
                 scale: glm.vec2 = glm.vec2(1, 1)):
        super().__init__()
        self._name = name
        self._position = position
        self.z = z
        self._rotation = rotation
        self._scale = scale
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, other: glm.vec2):
        self._position = other
        self.update()

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, other: float):
        self._rotation = other
        self.update()

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, other: glm.vec2):
        self._scale = other
        self.update()

    @property
    def matrix(self):
        return self._matrix

    def update(self):
        self._matrix = glm.scale(glm.rotate(glm.translate(glm.mat4(1.0), glm.vec3(self.position, 0)), glm.radians(self.rotation), glm.vec3(0, 0, 1)), glm.vec3(self.scale, 1.0))

    def __str__(self):
        return f"(Node name:\"{self.name}\" position:({self.position.x}, {self.position.y}), z-index:{self.z}, rotation:{self.rotation}, scale:({self.scale.x}, {self.scale.y}))"

    def __eq__(self, other: BaseNode):
        return self._name == other.name

    def draw(self):
        print(f"Drawing: {self.__str__()}")
        for child in self.children:
            child.draw()
