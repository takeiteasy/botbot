import asyncio
import pyray as r
from botbot import BotBot
from botbot.games import *
from botbot.scene import Transition
import random
import sys

class DefaultBot(BotBot):
    config = {
        "width": 1024,
        "height": 768,
        "title": "BotBot",
        "fps": 60
    }
    states = ["HorseRaces", "Roulette", "NextGame"]
    transitions = [Transition(trigger="next", source="*", dest="NextGame", after="setup_next")]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._scene = None
        self._last_scene = None

    def enter(self):
        self.next()

    def setup_next(self):
        if self._scene is not None:
            self._last_scene = self._scene.__class__.__name__
        available_states = [s for s in self.states[:-1] if s != self._last_scene]
        next_state = random.choice(available_states)
        if self._scene is not None:
            self._scene.exit()
        for module in sys.modules.values():
            if hasattr(module, next_state):
                SceneClass = getattr(module, next_state)
                break
        else:
            raise ValueError(f"Scene `{next_state}` not found")
        self._scene = SceneClass()
        self._scene.clear_color = getattr(SceneClass, 'background_color', r.RAYWHITE)
        self._scene.enter()
        self.fsm.set_state(next_state)

    def step(self, delta):
        if self._scene is not None:
            self._scene.step(delta)
        if r.is_key_pressed(r.KEY_SPACE):
            self.next()

    def draw(self):
        if self._scene is not None:
            self._scene.draw()
    
if __name__ == "__main__":
    bot = DefaultBot()
    asyncio.run(bot.run())