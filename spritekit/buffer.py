import moderngl as mgl
import numpy as np
from .disposable import Disposable
from typing import Union, Optional, List

class Vertex:
    @property
    def data(self):
        return np.array([vvv for vv in [v.to_list() for v in list(vars(self).values())] for vvv in vv])

class Buffer(Disposable):
    def __init__(self, data: Optional[Union[np.ndarray, List[np.ndarray]]] = None):
        self.buffer = None
        self.vbo = None
        if data:
            match data:
                case np.ndarray():
                    self.push(data)
                case list():
                    self.push(np.concatenate(data))
                case _:
                    raise ValueError("Expected numpy.ndarray or List[numpy.ndarray]")

    @property
    def empty(self):
        return self.buffer is None or not len(self.buffer)

    @property
    def valid(self):
        return self.vbo is not None

    def push(self, data: np.ndarray):
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
        self.buffer = None

    def release(self):
        if self.valid:
            self.vbo.release()
            self.vbo = None
