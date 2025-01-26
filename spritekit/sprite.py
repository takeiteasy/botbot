import moderngl as mgl
from .program import *
from .buffer import *
from .texture import *
from dataclasses import dataclass
import glm

class SpriteProgram(Program):
    vertex_source = """#version 330
                       layout (location = 0) in vec2 position;
                       layout (location = 1) in vec2 texcoord;
                       layout (location = 2) in vec4 color;

                       uniform mat4 world;
                       uniform mat4 projection;

                       out vec2 uv;
                       out vec4 col;

                       void main() {
                           gl_Position = world * projection * vec4(position, 0.0, 1.0);
                           uv = texcoord;
                           col = color;
                       }"""
    fragment_source = """#version 330 core
                         in vec2 uv;
                         in vec4 col;

                         uniform sampler2D smp;
                         out vec4 fragColor;

                         void main() {
                             fragColor = texture(smp, uv) * col;
                         }"""

@dataclass
class SpriteUniforms(Uniforms):
    world: glm.mat4
    projection: glm.mat4

@dataclass
class SpriteVertex(Vertex):
    position: glm.vec2
    texcoord: glm.vec2
    color: glm.vec4

class BaseNode:
    def __init__(self,
                 position: glm.vec2 = glm.vec2(0, 0),
                 z: float = 0,
                 rotation: float = 0,
                 scale: glm.vec2 = glm.vec2(1, 1)):
        self._position = position
        self.z = z
        self._rotation = rotation
        self._scale = scale
        self.update()

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
        return f"(BaseNode position:({self.position.x}, {self.position.y}), z-index:{self.z}, rotation:{self.rotation}, scale:({self.scale.x}, {self.scale.y}))"

class Sprite(BaseNode):
    def __init__(self, texture: Texture, **kwargs):
        super().__init__(**kwargs)
        self.texture = texture
