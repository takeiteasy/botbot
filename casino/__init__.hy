(import pyray *)
(import asyncio)
(import re)
(import twitchAPI.twitch [Twitch])
(import twitchAPI.oauth [UserAuthenticator])
(import twitchAPI.type [AuthScope ChatEvent])
(import twitchAPI.chat [Chat EventData ChatMessage ChatSub ChatCommand])
(import .database [connect-database clear-stakes])
(import .roulette *)

(defmacro read-file [path]
  `(.strip (.read (open ~path "r"))))

(defn :async run []
  (let [app-id (read-file "twitch-token.txt")
        app-secret (read-file "twitch-secret.txt")
        app-refresh (read-file "twitch-refresh.txt")
        app-access (read-file "twitch-access.txt")
        user-scope [AuthScope.CHAT_READ AuthScope.CHAT_EDIT]
        host-channel "bellowsroryb"
        twitch (await (Twitch app-id app-secret))]
    (await (twitch.set-user-authentication app-access user-scope app-secret))
    (let [chat (await (Chat twitch))]
      (connect-database)
      (clear-stakes)
      (chat.start)
      (init-window 1920 1080 "botbot")
      (set-target-fps 60)
      (while (not (window-should-close))
        (begin-drawing)
        (clear-background RAYWHITE)
        (draw-text "hello!" 10 10 20 RED)
        (end-drawing))

      (close-window))))
