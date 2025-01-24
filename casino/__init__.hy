(import pyray *)
(import asyncio)
(import re)
(import twitchAPI.twitch [Twitch])
(import twitchAPI.oauth [UserAuthenticator])
(import twitchAPI.type [AuthScope ChatEvent])
(import twitchAPI.chat [Chat EventData ChatMessage ChatSub ChatCommand])
(import .croupier *)

(defmacro read-file [path]
  `(.strip (.read (open ~path "r"))))

(defmacro reply [cmd msg]
  `(await (.reply ~cmd ~msg)))

(defclass Casino []
  (defn :async connect [self]
    (let [app-id (read-file "twitch-token.txt")
          app-secret (read-file "twitch-secret.txt")
          app-refresh (read-file "twitch-refresh.txt")
          app-access (read-file "twitch-access.txt")
          user-scope [AuthScope.CHAT_READ AuthScope.CHAT_EDIT]
          twitch (await (Twitch app-id app-secret))]
      (setv self.twitch (await (Twitch app-id app-secret)))
      (await (self.twitch.set-user-authentication app-access user-scope app-secret))
      (setv self.chat (await (Chat self.twitch)))
      (self.chat.register-event ChatEvent.READY self.on-ready)
      (self.chat.register-command "register" self.on-register)
      (self.chat.register-command "balance" self.on-balance)
      (self.chat.register-command "bet" self.on-bet)
      (self.chat.start))
    (setv self.croupier (Croupier)))

  (defn :async close [self]
    (self.chat.stop)
    (await (self.twitch.close)))

  (defn :async on-ready [self event]
    (await (event.chat.join-room (read-file "twitch-channel.txt"))))

  (defn :async on-register [self cmd]
    (try
      (create-user cmd.user.id)
      (except [e AlreadyRegisteredError]
        (reply cmd (str e)))
      (else
        (reply cmd f"You are now registered, your balance is ${**default-balance**}"))))

  (defn :async on-balance [self cmd]
    (let [player (find-user cmd.user.id)]
      (reply cmd (if player
                   (let [stake (current-user-stake player.uid)]
                     (if stake 
                       f"Your total balance is ${player.balance} with ${(- player.balance stake)} available"
                       f"Your balance is ${player.balance}"))
                   "You are not registered, please type `!register` to begin"))))

  (defn :async on-bet [self cmd]
    (reply cmd "whoa there fella")))

