(import pony.orm *)
(import redis [Redis])
(import queue [Queue])

(setv
  **db** (Database)
  **cache** (Redis "localhost" 6379 0)
  **default-balance** 1000)

(defn clear-stakes []
  (.delete **cache** "stakes"))

(defn connect-database []
  (.bind **db** :provider "sqlite"
                :filename "botbot.db"
                :create-db True)
  (.generate-mapping **db** :create_tables True))

(defclass Player [**db**.Entity]
  (setv
    id (PrimaryKey int :auto True)
    uid (Required int :unique True)
    balance (Required int)))

(defmacro with-db [#* body]
  `(with [db-session]
     ~@body
     (commit)))

(defclass InvalidUserError [Exception]
  (defn __str__ [self]
    "You are not registered, type `!register` to begin"))

(defclass AlreadyRegisteredError [Exception]
  (defn __str__ [self]
    "You are already registered"))

(defclass InsufficientFundsError [Exception]
  (defn __init__ [self amount total]
    (setv
      self.amount amount
      self.total total)
    (Exception.__init__ self))

  (defn __str__ [self]
    f"Cannot place bet for `${self.amount}` you only have `${self.total}` available"))

(defclass Bet []
  (defn __init__ [self user amount [multiplier 1]]
    (setv
      self.user user
      self.amount amount
      self.multiplier multiplier))

  (defn __str__ [self]
    f"(Bet uid:{self.user} risk:{self.amount} return:{(* self.amount self.multiplier)})"))

(defn find-user [uid]
  (let [result None]
    (with-db
      (setv result (.get Player :uid uid)))
    result))

(defn create-user [uid]
  (if (find-user uid)
    (raise AlreadyRegisteredError)
    (with-db
      (Player :uid uid
              :balance **default-balance**))))

(defn current-user-stake [uid]
  (if (.hexists **cache** "stakes" uid)
    (int (.hget **cache** "stakes" uid))
    0))

(defclass Croupier []
  (defn __init__ [self]
    (clear-stakes)
    (connect-database)
    (setv self.bets (Queue)))

  (defn take-bet [self bet]
    (let [player (find-user bet.user)]
      (cond
        (not player) (raise InvalidUserError)
        (< (- player.balance (current-user-stake bet.user)) 0) (raise InsufficientFundsError)
        _ (self.bets.put bet)))))
