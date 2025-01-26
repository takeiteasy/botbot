from PIL import Image
import moderngl as mgl
from os.path import exists, isfile
from .disposable import Disposable

class Texture(Disposable):
    def __init__(self, ctx, path: str = None, image: Image = None):
        self.ctx = ctx
        self.texture = None
        self.sampler = None
        self._image = None
        self._width = 0
        self._height = 0
        self._image = None
        if path is not None:
            try:
                self.load(path)
            except FileNotFoundError as e:
                if not image:
                    raise e
        if not self._image and image:
            self.copy(image)

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

    def copy(self, new_image: Image):
        self._image = new_image
        self._width = self.image.width
        self._height = self.image.height
        self.compile()

    @image.setter
    def image(self, new_image: Image):
        self.copy(new_image)

    def load(self, path, store_original=True):
        if not exists(path) or not isfile(path):
            raise FileNotFoundError(path)
        self.image = Image.open(path).convert('RGBA')
        self.compile()

    def compile(self):
        if self.valid:
            self.release()
        self.texture = self.ctx.texture(self.image.size, 4, self.image.tobytes())
        self.sampler = self.ctx.sampler(texture=self.texture)
        self.sampler.filter = (mgl.NEAREST, mgl.NEAREST)

    def use(self, location=None, sampler_location=0, texture_location=0):
        if self.valid:
            self.sampler.use(location=location if location else sampler_location)
            self.texture.use(location=location if location else texture_location)

    def release(self):
        if self.texture is not None:
            self.texture.release()
            self.texture = None
        if self.sampler is not None:
            self.sampler.release()
            self.texture = None
