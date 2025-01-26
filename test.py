import spritekit as sk
import pygame as pg

with sk.window() as window:
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
