import moderngl as mgl
from glsl_shaderinfo import get_info
from .disposable import Disposable

class Program(Disposable):
    vertex_source = None
    fragment_source = None

    def __init__(self):
        self.vs_uniforms = {}
        self.fs_uniforms = {}
        self.vs_in = {}
        self.vs_out = {}
        self.fs_in = {}
        self.fs_out = {}
        self.program = None
        self.compile()

    def compile(self):
        if self.vertex_source is None or self.fragment_source is None:
            raise ValueError("Vertex source or fragment source not set")
        vertex_info = get_info(self.vertex_source)
        fragment_info = get_info(self.fragment_source)
        def get_values(arr):
            return { k: v for k, v in [(i.name, i.type_specifier) for i in arr]}
        self.vs_uniforms = get_values(vertex_info.uniforms)
        self.fs_uniforms = get_values(fragment_info.uniforms)
        self.vs_in = get_values(vertex_info.inputs)
        self.vs_out = get_values(vertex_info.outputs)
        self.fs_in = get_values(fragment_info.inputs)
        self.fs_out = get_values(fragment_info.outputs)
        self.program = mgl.get_context().program(self.vertex_source, self.fragment_source)

        @property
        def attr_layout(self):
            types = []
            names = []
            for name, type_spec in self.vs_in.items():
                match type_spec:
                    case 'Vec2':
                        type_spec = '2f'
                    case 'Vec3':
                        type_spec = '3f'
                    case 'Vec4':
                        type_spec = '4f'
                    case _:
                        raise ValueError(f"Unknown shader attribute: {name}, {type_spec}")
                names.append(name)
                types.append(type_spec)
            return names, ' '.join(types)

    @property
    def valid(self):
        return self.program is not None

    def release(self):
        if self.valid:
            self.program.release()
            self.program = None

class Uniforms:
    def __getitem__(self, index):
        if not hasattr(self, index):
            raise ValueError(f"Invalid uniform {index}")
        return getattr(self, index)

    def __setitem__(self, index):
        if not hasattr(self, index):
            raise ValueError(f"Invalid uniform {index}")
        setattr(self, index)

    def apply(self, program: Program):
        for key in list(vars(self).keys()):
            program.program[key].write(getattr(self, key))
