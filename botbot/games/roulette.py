from ..scene import Scene
import pyray as r

class Roulette(Scene):
    background_color = (0, 0, 255, 255)

    def enter(self):
        pass

    def step(self, delta):
        super().step(delta)
    
    def draw(self):
        super().draw()