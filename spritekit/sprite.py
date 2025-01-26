import moderngl as mgl
from .program import *
from .buffer import *
from .texture import *
from .base import *
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

class Sprite(BaseNode):
    def __init__(self, texture: Texture, **kwargs):
        super().__init__(**kwargs)
        self.texture = texture
