import spritekit as sk
import pygame as pg
import glm

class TestScene(sk.Scene):
    def __init__(self):
        super().__init__()

with sk.window() as window:
    test = sk.Sprite(None, position=glm.vec2(2,2), z=10, rotation=50)
    print(test)
    for delta in window.loop():
        for event in window.poll:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                window.quit()
