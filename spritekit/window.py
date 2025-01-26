import pygame as pg
import pygame._sdl2
from typing import Tuple
from contextlib import contextmanager
import moderngl as mgl
from imgui.integrations.base import BaseOpenGLRenderer
import imgui
import time
import ctypes
import glm

class ModernGLRenderer(BaseOpenGLRenderer):
    VERTEX_SHADER_SRC = """
        #version 330
        uniform mat4 ProjMtx;
        in vec2 Position;
        in vec2 UV;
        in vec4 Color;
        out vec2 Frag_UV;
        out vec4 Frag_Color;
        void main() {
            Frag_UV = UV;
            Frag_Color = Color;
            gl_Position = ProjMtx * vec4(Position.xy, 0, 1);
        }
    """
    FRAGMENT_SHADER_SRC = """
        #version 330
        uniform sampler2D Texture;
        in vec2 Frag_UV;
        in vec4 Frag_Color;
        out vec4 Out_Color;
        void main() {
            Out_Color = (Frag_Color * texture(Texture, Frag_UV.st));
        }
    """

    def __init__(self, wnd, ctx):
        self._prog = None
        self._fbo = None
        self._font_texture = None
        self._vertex_buffer = None
        self._index_buffer = None
        self._vao = None
        self._textures = {}
        self.wnd = wnd
        self.ctx = ctx

        if not self.ctx:
            raise ValueError("Missing moderngl context")

        assert isinstance(self.ctx, mgl.Context)

        super().__init__()

        self.io.display_size = self.wnd.size
        self.io.display_fb_scale = (1, 1)

    def register_texture(self, texture: mgl.Texture):
        """Make the imgui renderer aware of the texture"""
        self._textures[texture.glo] = texture

    def remove_texture(self, texture: mgl.Texture):
        """Remove the texture from the imgui renderer"""
        del self._textures[texture.glo]

    def refresh_font_texture(self):
        width, height, pixels = self.io.fonts.get_tex_data_as_rgba32()

        if self._font_texture:
            self.remove_texture(self._font_texture)
            self._font_texture.release()

        self._font_texture = self.ctx.texture((width, height), 4, data=pixels)
        self.register_texture(self._font_texture)
        self.io.fonts.texture_id = self._font_texture.glo
        self.io.fonts.clear_tex_data()

    def _create_device_objects(self):
        self._prog = self.ctx.program(
            vertex_shader=self.VERTEX_SHADER_SRC,
            fragment_shader=self.FRAGMENT_SHADER_SRC,
        )
        self.projMat = self._prog["ProjMtx"]
        self._prog["Texture"].value = 0
        self._vertex_buffer = self.ctx.buffer(reserve=imgui.VERTEX_SIZE * 65536)
        self._index_buffer = self.ctx.buffer(reserve=imgui.INDEX_SIZE * 65536)
        self._vao = self.ctx.vertex_array(
            self._prog,
            [(self._vertex_buffer, "2f 2f 4f1", "Position", "UV", "Color")],
            index_buffer=self._index_buffer,
            index_element_size=imgui.INDEX_SIZE,
        )

    def render(self, draw_data):
        io = self.io
        display_width, display_height = io.display_size
        fb_width = int(display_width * io.display_fb_scale[0])
        fb_height = int(display_height * io.display_fb_scale[1])

        if fb_width == 0 or fb_height == 0:
            return

        self.projMat.value = (
            2.0 / display_width,
            0.0,
            0.0,
            0.0,
            0.0,
            2.0 / -display_height,
            0.0,
            0.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            -1.0,
            1.0,
            0.0,
            1.0,
        )

        draw_data.scale_clip_rects(*io.display_fb_scale)

        self.ctx.enable_only(mgl.BLEND)
        self.ctx.blend_equation = mgl.FUNC_ADD
        self.ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA

        self._font_texture.use()

        for commands in draw_data.commands_lists:
            # Write the vertex and index buffer data without copying it
            vtx_type = ctypes.c_byte * commands.vtx_buffer_size * imgui.VERTEX_SIZE
            idx_type = ctypes.c_byte * commands.idx_buffer_size * imgui.INDEX_SIZE
            vtx_arr = vtx_type.from_address(commands.vtx_buffer_data)
            idx_arr = idx_type.from_address(commands.idx_buffer_data)
            self._vertex_buffer.write(vtx_arr)
            self._index_buffer.write(idx_arr)

            idx_pos = 0
            for command in commands.commands:
                texture = self._textures.get(command.texture_id)
                if texture is None:
                    raise ValueError(
                        (
                            "Texture {} is not registered. Please add to renderer using "
                            "register_texture(..). "
                            "Current textures: {}".format(
                                command.texture_id, list(self._textures)
                            )
                        )
                    )

                texture.use(0)

                x, y, z, w = command.clip_rect
                self.ctx.scissor = int(x), int(fb_height - w), int(z - x), int(w - y)
                self._vao.render(
                    mgl.TRIANGLES, vertices=command.elem_count, first=idx_pos
                )
                idx_pos += command.elem_count

        self.ctx.scissor = None

    def _invalidate_device_objects(self):
        if self._font_texture:
            self._font_texture.release()
        if self._vertex_buffer:
            self._vertex_buffer.release()
        if self._index_buffer:
            self._index_buffer.release()
        if self._vao:
            self._vao.release()
        if self._prog:
            self._prog.release()

        self.io.fonts.texture_id = 0
        self._font_texture = None

class PygameRenderer(ModernGLRenderer):
    def __init__(self, ctx):
        self.wnd = pygame._sdl2.video.Window.from_display_module()
        super(PygameRenderer, self).__init__(self.wnd, ctx)

        self._gui_time = None
        self.custom_key_map = {}

        self._map_keys()

    def _custom_key(self, key):
        # We need to go to custom keycode since imgui only support keycod from 0..512 or -1
        if not key in self.custom_key_map:
            self.custom_key_map[key] = len(self.custom_key_map)
        return self.custom_key_map[key]

    def _map_keys(self):
        key_map = self.io.key_map

        key_map[imgui.KEY_TAB] = self._custom_key(pg.K_TAB)
        key_map[imgui.KEY_LEFT_ARROW] = self._custom_key(pg.K_LEFT)
        key_map[imgui.KEY_RIGHT_ARROW] = self._custom_key(pg.K_RIGHT)
        key_map[imgui.KEY_UP_ARROW] = self._custom_key(pg.K_UP)
        key_map[imgui.KEY_DOWN_ARROW] = self._custom_key(pg.K_DOWN)
        key_map[imgui.KEY_PAGE_UP] = self._custom_key(pg.K_PAGEUP)
        key_map[imgui.KEY_PAGE_DOWN] = self._custom_key(pg.K_PAGEDOWN)
        key_map[imgui.KEY_HOME] = self._custom_key(pg.K_HOME)
        key_map[imgui.KEY_END] = self._custom_key(pg.K_END)
        key_map[imgui.KEY_INSERT] = self._custom_key(pg.K_INSERT)
        key_map[imgui.KEY_DELETE] = self._custom_key(pg.K_DELETE)
        key_map[imgui.KEY_BACKSPACE] = self._custom_key(pg.K_BACKSPACE)
        key_map[imgui.KEY_SPACE] = self._custom_key(pg.K_SPACE)
        key_map[imgui.KEY_ENTER] = self._custom_key(pg.K_RETURN)
        key_map[imgui.KEY_ESCAPE] = self._custom_key(pg.K_ESCAPE)
        key_map[imgui.KEY_PAD_ENTER] = self._custom_key(pg.K_KP_ENTER)
        key_map[imgui.KEY_A] = self._custom_key(pg.K_a)
        key_map[imgui.KEY_C] = self._custom_key(pg.K_c)
        key_map[imgui.KEY_V] = self._custom_key(pg.K_v)
        key_map[imgui.KEY_X] = self._custom_key(pg.K_x)
        key_map[imgui.KEY_Y] = self._custom_key(pg.K_y)
        key_map[imgui.KEY_Z] = self._custom_key(pg.K_z)

    def process_event(self, e):
        # perf: local for faster access
        io = self.io

        match e.type:
            case pg.MOUSEMOTION:
                io.mouse_pos = e.pos
            case pg.MOUSEBUTTONDOWN | pg.MOUSEBUTTONUP:
                if e.button < 1 or e.button > 3:
                    return False
                else:
                    io.mouse_down[e.button - 1] = e.type == pg.MOUSEBUTTONDOWN
            case pg.KEYDOWN:
                for char in e.unicode:
                    code = ord(char)
                    if 0 < code < 0x10000:
                        io.add_input_character(code)
                        io.keys_down[self._custom_key(e.key)] = True
            case pg.KEYDOWN | pg.KEYUP:
                if e.type == pg.KEYUP:
                    io.keys_down[self._custom_key(e.key)] = False
                    io.key_ctrl = (
                        io.keys_down[self._custom_key(pg.K_LCTRL)] or
                        io.keys_down[self._custom_key(pg.K_RCTRL)]
                    )
                    io.key_alt = (
                        io.keys_down[self._custom_key(pg.K_LALT)] or
                        io.keys_down[self._custom_key(pg.K_RALT)]
                    )
                    io.key_shift = (
                        io.keys_down[self._custom_key(pg.K_LSHIFT)] or
                        io.keys_down[self._custom_key(pg.K_RSHIFT)]
                    )
                    io.key_super = (
                        io.keys_down[self._custom_key(pg.K_LSUPER)] or
                        io.keys_down[self._custom_key(pg.K_LSUPER)]
                    )
            case pg.VIDEORESIZE:
                surface = pg.display.get_surface()
                # note: pg does not modify existing surface upon resize,
                #       we need to to it ourselves.
                pygame.display.set_mode(
                    (e.w, e.h),
                    flags=surface.get_flags(),
                )
                # existing font texure is no longer valid, so we need to refresh it
                self.refresh_font_texture()
                # notify imgui about new window size
                io.display_size = e.size
                # delete old surface, it is no longer needed
                del surface
            case _:
                return False
        return True

    def process_inputs(self):
        io = imgui.get_io()

        current_time = pg.time.get_ticks() / 1000.0

        if self._gui_time:
            io.delta_time = current_time - self._gui_time
        else:
            io.delta_time = 1. / 60.
        if io.delta_time <= 0.0:
            io.delta_time = 1./ 1000.
            self._gui_time = current_time

class Window:
    def __init__(self, width: int, height: int, title: str, flags: int):
        self._width = width
        self._height = height
        self._title = title
        self._flags = flags
        self._open = True
        self._clear_color = (0, 0, 0)
        self._projection = None

        self._ctx = mgl.get_context()
        imgui.create_context()
        self.imgui_ctx = PygameRenderer(self.ctx)

    @property
    def ctx(self):
        return self._ctx

    @property
    def size(self) -> Tuple[int, int]:
        return self._width, self._height

    @size.setter
    def size(self, width, height):
        self.resize(width, height)

    @property
    def open(self) -> bool:
        return self._open

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title: str):
        self._title = title
        pg.display.set_caption(title)

    @property
    def flags(self):
        return self._flags

    @flags.setter
    def flags(self, new_flags):
        self.resize(self._width, self._height, flags=new_flags)

    def resize(self, width: int, height: int, flags=None):
        if self._width != width:
            self._width = width
            self._projection = None
        if self._height != height:
            self._height = height
            self._projection = None
        if flags is None:
            flags = self._flags
            self._flags = flags
            pg.display.set_mode((width, height), flags=flags)

    @property
    def projection(self):
        return self._projection

    @projection.getter
    def projection(self):
        if not self._projection:
            self._projection = glm.ortho(0, self._width, self._height, 0, -1, 1)
        return self._projection

    @property
    def poll(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._open = False
            else:
                used = False
                if event.type == pg.VIDEORESIZE:
                    self._width = event.w
                    self._height = event.h
                    used = self.imgui_ctx.process_event(event)
                if not used or not imgui.is_window_hovered(imgui.HOVERED_ANY_WINDOW):
                    yield event
                    self.imgui_ctx.process_inputs()

    @property
    def clear_color(self):
        return self._clear_color

    def set_clear_color(self, r, g, b):
        self._clear_color = (r, g, b)

    def loop(self, frame_limit=None):
        prev_time = time.perf_counter()
        current_time = prev_time
        step = 0 if frame_limit is None else 1.0 / frame_limit
        count = 0
        accum = 0
        while self.open:
            prev_time = current_time
            current_time = time.perf_counter()
            dt = current_time - prev_time
            if frame_limit is not None:
                accum += dt
                count += 1
                if accum >= 1.0:
                    accum -= 1.0
                    count = 0
                while time.perf_counter() < current_time + step:
                    pass

            self._ctx.clear(self._clear_color[0], self._clear_color[1], self.clear_color[2])
            imgui.new_frame()
            yield dt
            imgui.end_frame()
            imgui.render()
            self.imgui_ctx.render(imgui.get_draw_data())
            pg.display.flip()

    def quit(self):
        self._open = False

@contextmanager
def window(size: Tuple[int, int] = None,
           title: str = "spritekit",
           flags: int = pg.OPENGL | pg.DOUBLEBUF | pg.NOFRAME,
           gl_version: Tuple[int, int] = (3, 3)):
    pg.init()
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, gl_version[0])
    pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, gl_version[1])
    pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
    pg.display.gl_set_attribute(pg.GL_DOUBLEBUFFER, 1)
    pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)
    pg.display.gl_set_attribute(pg.GL_STENCIL_SIZE, 8)
    pg.display.set_caption(title)
    if not size:
        info = pg.display.Info()
        size = (info.current_w, info.current_h)
        pg.display.set_mode(size, flags=flags, vsync=True)
        yield Window(size[0], size[1], title, flags)
        pg.quit()
