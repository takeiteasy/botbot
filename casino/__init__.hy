(import pyray *)
(import asyncio)
(import re)
(import twitchAPI.twitch [Twitch])
(import twitchAPI.oauth [UserAuthenticator])
(import twitchAPI.type [AuthScope ChatEvent])
(import twitchAPI.chat [Chat EventData ChatMessage ChatSub ChatCommand])
(import .database *)
(import .roulette *)

(defmacro read-file [path]
  `(.strip (.read (open ~path "r"))))

(defn :async on-ready [event]
  (await (event.chat.join-room "bellowsroryb")))

(defn :async on-register [cmd]
  (if (find-user cmd.user.id)
    (await (cmd.reply "You are already registered"))
    (do
      (new-user cmd.user.id)
      (await (cmd.reply f"You are now registered, your balance is ${**default-balance**}")))))

(defn :async on-balance [cmd]
  (let [player (find-user cmd.user.id)]
    (await (cmd.reply (if player
                        (let [stake (current-user-stake player.uid)]
                          (if (> stake 0)
                            f"Your total balance is ${player.balance} with ${(- player.balance stake)} available"
                            f"Your balance is ${player.balance}"))
                        "You are not registered, please type `!register` to begin")))))

(defn :async run []
  (let [app-id (read-file "twitch-token.txt")
        app-secret (read-file "twitch-secret.txt")
        app-refresh (read-file "twitch-refresh.txt")
        app-access (read-file "twitch-access.txt")
        user-scope [AuthScope.CHAT_READ AuthScope.CHAT_EDIT]
        twitch (await (Twitch app-id app-secret))]
    (await (twitch.set-user-authentication app-access user-scope app-secret))
    (let [chat (await (Chat twitch))]
      (connect-database)
      (clear-stakes)
      (chat.register-event ChatEvent.READY on-ready)
      (chat.register-command "register" on-register)
      (chat.register-command "balance" on-balance)
      (chat.start)
      (init-window 1920 1080 "botbot")
      (set-target-fps 60)
      (while (not (window-should-close))
        (begin-drawing)
        (clear-background RAYWHITE)
        (draw-text "hello!" 10 10 20 RED)
        (end-drawing))
      (chat.stop)
      (close-window)
      (await (twitch.close)))))
