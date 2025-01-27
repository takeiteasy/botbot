import moderngl as mgl
import numpy as np
from .disposable import Disposable
from typing import Optional

class Vertex:
    @property
    def data(self):
        return np.array([vvv for vv in [v.to_list() for v in list(vars(self).values())] for vvv in vv])

class Buffer(Disposable):
    def __init__(self, data: Optional[np.array] = None):
        self.buffer = None
        self.vbo = None
        if data:
            self.push(data)

    @property
    def empty(self):
        return self.buffer is None or not len(self.buffer)

    @property
    def valid(self):
        return self.vbo is not None

    def push(self, data: np.array):
        if not self.buffer:
            self.buffer = bytearray()
            self.buffer.extend(data.astype('f4').tobytes())

    def compile(self):
        if self.empty:
            raise ValueError("Vertex buffer is empty")
        if self.valid:
            self.release()
        self.vbo = mgl.get_context().buffer(self.buffer)

    def clear(self):
        self.buffer = bytearray()

    def release(self):
        if self.valid:
            self.vbo.release()
            self.vbo = None
