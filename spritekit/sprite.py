from PIL import Image
import moderngl as mgl
from os.path import exists, isfile
from .program import *
from .buffer import *
from dataclasses import dataclass
from typing import Optional
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

def generate_quad(self, position: glm.vec2, rotation: Optional[float] = 0, size: Optional[glm.vec2] = None, clip: Optional[glm.vec4] = None, color=glm.vec4(1, 1, 1, 1)):
    min_x = position.x
    min_y = position.y
    img_sz = glm.vec2(self.texture.width, self.texture.height)
    sz = size if size is not None else img_sz if clip is None else clip.zw
    max_x = position.x + sz.x
    max_y = position.y + sz.y
    center = glm.vec2((min_x + max_x) / 2,
                      (min_y + max_y) / 2)
    corners = [glm.vec2(min_x - center.x, min_y - center.y),
               glm.vec2(max_x - center.x, min_y - center.y),
               glm.vec2(max_x - center.x, max_y - center.y),
               glm.vec2(min_x - center.x, max_y - center.y)]
    if rotation != 0:
        ct = math.cos(rotation)
        st = math.sin(rotation)
        for i in range(len(corners)):
            x = corners[i].x
            y = corners[i].y
            corners[i].x = x * ct - y * st
            corners[i].y = x * st + y * ct
    for i in range(len(corners)):
        corners[i].x += center.x
        corners[i].y += center.y
    if clip is None:
        texcoords = [glm.vec2(0.0, 0.0),
                     glm.vec2(1.0, 0.0),
                     glm.vec2(1.0, 1.0),
                     glm.vec2(0.0, 1.0)]
    else:
        normalized_pos = glm.vec2(clip.x, clip.y) / img_sz
        normalized_size = glm.vec2(clip.z, clip.w) / img_sz
        texcoords = [normalized_pos,
                     normalized_pos + glm.vec2(normalized_size.x, 0),
                     normalized_pos + normalized_size,
                     normalized_pos + glm.vec2(0, normalized_size.y)]
        vcol = color or self.color
    return [SpriteVertex(position=corners[i], texcoord=texcoords[i], color=vcol) for i in [0, 1, 2, 2, 3, 0]]

class Sprite(Disposable):
    def __init__(self, ctx, path: str = None, image: Image = None):
        self.ctx = ctx
        self.texture = None
        self.sampler = None
        self._image = None
        self._width = 0
        self._height = 0
        if image is not None:
            self.image = image
        if path is not None:
            self.load(path)

    @property
    def valid(self):
        return self.sampler is not None and self.texture is not None

    @property
    def size(self):
        return self._width, self._height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new_image: Image):
        self._image = new_image
        self._width = self.image.width
        self._height = self.image.height
        self.compile()

    def load(self, path, store_original=True):
        if not exists(path) or not isfile(path):
            raise FileNotFoundError(path)
        self.image = Image.open(path).convert('RGBA')
        self.compile()

    def compile(self):
        if self.valid:
            self.texture.release()
            self.sampler.release()
            self.texture = self.ctx.texture(self.image.size, 4, self.image.tobytes())
            self.sampler = self.ctx.sampler(texture=self.texture)
            self.sampler.filter = (mgl.NEAREST, mgl.NEAREST)

    def use(self):
        if self.valid:
            self.sampler.use()

    def release(self):
        if self.texture is not None:
            self.texture.release()
            self.texture = None
        if self.sampler is not None:
            self.sampler.release()
            self.texture = None
