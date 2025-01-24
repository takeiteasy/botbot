import moderngl as mgl
import numpy as np
from .disposable import Disposable

class Buffer(Disposable):
    def __init__(self, ctx: mgl.Context, layout: str = ""):
        self.ctx = ctx
        self.buffer = None 
        self.vbo = None

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
        self.vbo = self.ctx.buffer(self.buffer)
    
    def clear(self):
        self.buffer = bytearray()

    def release(self):
        if self.valid:
            self.vbo.release()
            self.vbo = None
