(import pony.orm *)
(import redis [Redis])
(import queue [Queue])

(setv
  **db** (Database)
  **cache** (Redis "localhost" 6379 0)
  **default-balance** 1000
  **bets** (Queue))

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

(defmacro defn/db [name params #* body]
  `(defn ~name ~params
     ~(let [result (hy.gensym)]
        `(do
           (with-db
             (setv ~result ~@body))
           ~result))))

(defn/db find-user [uid]
         (.get Player :uid uid))

(defn/db new-user [uid]
         (Player :uid uid :balance **default-balance**))

(defn resolve-user-stakes []
  (with-db
    (for [[k v] (.hscan-iter **cache** "stakes")]
      (let [player (.get Player :uid (int k))]
        (when player
          (setv player.balance (- player.balance (int v)))))))
  (clear-stakes))

(defn resolve-user-bets [winner]
  (with-db
    (while (not (.empty **bets**))
      (let [bet (.get **bets**)
            player (.get Player :uid bet.user)]
        (when (and player (in winner bet.numbers))
          (setv player.balance (+ player.balance (+ bet.amount (* bet.amount bet.multiplier)))))))))

(defn current-user-stake [uid]
  (if (.hexists **cache** "stakes" uid)
    (int (.hget **cache** "stakes" uid))
    0))

(defn append-stake [uid amount]
  (if (.hexists **cache** "stakes" uid)
    (.hincrby **cache** "stakes" uid amount)
    (.hset **cache** "stakes" uid amount)))

(defclass InvalidUser [Exception]
  (defn __str__ [self]
    "You are not registered, type `!register` to start!"))

(defclass InsufficientFundsError [Exception]
  (defn __init__ [self amount total]
    (setv
      self.amount amount
      self.total total)
    (Exception.__init__ self))

  (defn __str__ [self]
    f"Cannot place bet for `${self.amount}` you only have `${self.total}` available"))
