import moderngl as mgl
from .program import *
from .buffer import *
from .texture import *
from .base import *
from .node import *
from dataclasses import dataclass
from typing import Union, Optional
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

class Sprite(Node, Disposable):
    vertices = [
            SpriteVertex(position=glm.vec2(-0.5,  0.5), texcoord=glm.vec2(0.0, 1.0), color=glm.vec4(1.0, 1.0, 1.0, 1.0)),
            SpriteVertex(position=glm.vec2( 0.5,  0.5), texcoord=glm.vec2(1.0, 1.0), color=glm.vec4(1.0, 1.0, 1.0, 1.0)),
            SpriteVertex(position=glm.vec2(-0.5, -0.5), texcoord=glm.vec2(0.0, 0.0), color=glm.vec4(1.0, 1.0, 1.0, 1.0)),
            SpriteVertex(position=glm.vec2( 0.5, -0.5), texcoord=glm.vec2(1.0, 0.0), color=glm.vec4(1.0, 1.0, 1.0, 1.0))]

    def __init__(self, texture: Union[str, Texture], owned: Optional[bool] = False, **kwargs):
        super().__init__(**kwargs)
        self.owned = owned
        match texture:
            case str():
                self.texture = Texture(image="test.png")
                self.owned = True
            case Texture():
                self.texture = texture
            case _:
                self.texture = None
        self.texture = texture
        self.buffer = Buffer(Sprite.vertices.data)
        self.buffer.compile()

    def draw(self):
        for child in self.children:
            child.draw()

    def release(self):
        if self.texture.valid and self.owned:
            del self.texture
        if self.buffer:
            del self.buffer
