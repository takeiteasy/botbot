import asyncio
from typing import Optional, Union

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatCommand, ChatSub, AuthScope, ChatEvent
from redis import Redis
from queue import Queue
import pyray as r
from pony.orm import *
from .scene import Scene

_DATABASE = Database()
_CACHE = Redis("localhost", 6379, 0)
_DEFAULT_BALANCE = 1000

class Player(_DATABASE.Entity):
    id = PrimaryKey(int, auto=True)
    uid = Required(int, unique=True)
    balance = Required(int, default=_DEFAULT_BALANCE)

class Bet:
    def __init__(self, player, amount, multiplier=1.):
        self.player = player
        self.amount = amount
        self.multiplier = multiplier

    def __str__(self):
        return f"({self.player.uid}: {self.amount}, {self.multiplier})"

class AlreadyRegisteredError(Exception):
    def __str__(self):
        return "You are already registered"

class InvalidUserError(Exception):
    def __str__(self):
        return "You are not registered, type `!register` to begin"

class InsufficientBalanceError(Exception):
    def __init__(self, balance: int, amount: int):
        self.balance = balance
        self.amount = amount
        super().__init__()

    def __str__(self):
        return f"Cannot place bet for `${self.amount}`, only `${self.total}` available"

def _find_user(uid: int) -> Player:
    with db_session:
        return Player.get(uid=uid)

def _create_user(uid: int) -> Player:
    if _find_user(uid) is not None:
        raise AlreadyRegisteredError()
    with db_session:
        return Player(uid=uid)

def _user_stake(uid: int) -> int:
    if (_CACHE.hexists("stakes", str(uid))):
        return int(_CACHE.hget("stakes", str(uid)))
    else:
        return 0

def _clear_stakes():
    _CACHE.delete("stakes")

def _connect_database():
    _DATABASE.bind(provider="sqlite", filename="botbot.db", create_db=True)
    _DATABASE.generate_mapping(create_tables=True)

def _read_file(s: str | None) -> str:
    if s is None:
        return None
    if s.endswith(".txt"):
        with open(s, "r") as f:
            return f.read().strip()
    else:
        return s

class BotBot(Scene):
    def __init__(self, app_id: Union[str, None] = None, app_secret: Union[str, None] = None, app_refresh: Union[str, None] = None, app_access: Union[str, None] = None, **kwargs):
        super().__init__(**kwargs)
        self.chat = None
        self.twitch = None
        self.app_id = _read_file(app_id)
        self.app_secret = _read_file(app_secret)
        self.app_refresh = _read_file(app_refresh)
        self.app_access = _read_file(app_access)
    
    async def quit(self):
        r.close_audio_device()
        r.close_window()
        # self.chat.stop()
        # await self.twitch.close()

    async def run(self):
        # user_scopes = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]
        # self.twitch = await Twitch(client_id=self.app_id, client_secret=self.app_secret)
        # await self.twitch.set_user_authentication(self.app_access, user_scopes, self.app_secret)
        # self.chat = await Chat(self.twitch)
        # self.chat.register_event(ChatEvent.READY, self.on_ready)
        # self.chat.register_command("register", self.on_register)
        # self.chat.register_command("balance", self.on_balance)
        # self.chat.register_command("bet", self.on_bet)
        # self.chat.start()

        r.init_window(self.config['width'] if "width" in self.config else 1024,
                      self.config['height'] if "height" in self.config else 768,
                      self.config['title'] if "title" in self.config else "BotBot")
        r.set_config_flags(self.config['flags'] if "flags" in self.config else 0)
        r.init_audio_device()
        if "fps" in self.config:
            r.set_target_fps(self.config['fps'])
        if "exit_key" in self.config:
            r.set_exit_key(self.config['exit_key'])
        self.enter()
        while not r.window_should_close():
            dt = r.get_frame_time()
            self.step(dt)
            r.begin_drawing()
            self.draw()
            r.end_drawing()
        await self.quit()

    async def on_ready(self, data: EventData):
        pass

    async def on_register(self, data: ChatCommand):
        pass

    async def on_balance(self, data: ChatCommand):
        pass

    async def on_bet(self, data: ChatCommand):
        pass