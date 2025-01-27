import spritekit as sk
import pygame as pg
import glm

class TestScene(sk.Scene):
    def enter(self):
        self.test = sk.Texture(self.ctx, path="test.png")
        self.add_child(sk.Sprite(self.test, name="test"))

    def event(self, e):
        pass

    def step(self, delta):
        pass

with sk.window() as window:
    scene = TestScene(window.ctx)
    scene.enter()
    for delta in window.loop():
        for event in window.poll:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                window.quit()
            else:
                scene.event(event)
        scene.step(delta)
        scene.draw()
    scene.exit()
