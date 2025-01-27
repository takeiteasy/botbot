import spritekit as sk
import pygame as pg
import glm

class TestScene(sk.Scene):
    def enter(self):
        self.test = sk.Texture(image="test.png")
        self.node = sk.Sprite(self.test, name="test")
        a = sk.Sprite(self.test, name="a")
        a.add_children([sk.Sprite(self.test, name="a"),
                        sk.Sprite(self.test, name="b"),
                        sk.Sprite(self.test, name="c")])
        self.node.add_children([a,
                                sk.Sprite(self.test, name="b"),
                                sk.Sprite(self.test, name="c")])
        self.add_child(self.node)

    def event(self, e):
        pass

    def step(self, delta):
        pass

with sk.window() as window:
    scene = TestScene()
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
