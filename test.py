import spritekit as sk
import pygame as pg
import glm

with sk.window() as window:
    sprite_prog = sk.SpriteProgram(window.ctx)
    sprite_ref = sk.Sprite(window.ctx, path="test.png")
    for delta in window.loop():
        for event in window.poll:
            match event.type:
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_ESCAPE:
                            window.quit()
                        case _:
                            print(event.key)
                case _:
                    print(event)
        sprite_ref.draw(sprite_prog, glm.mat4(1), window.projection, glm.vec2(32, 32), size=glm.vec2(32, 32), clip=glm.vec4(0, 32, 32, 32))
