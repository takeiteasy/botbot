(import .database *)
(import queue [Queue])

(defclass Bet []
  (defn __init__ [self user amount [multiplier 1]]
    (setv
      self.user user
      self.amount amount
      self.multiplier multiplier))
  
  (defn __str__ [self]
    f"(Bet uid:{self.user} risk:{self.amount} return:{(+ self.amount (* self.amount self.multiplier))})"))

(defclass Croupier []
  (defn __init__ [self]
    (setv self.bets (Queue)))

  (defn process-bets [self]
    (while (not (self.bets.empty))
      (print (self.bets.get))))

  (defn take-bet [self bet]
    (self.bets.put bet))
  
  (defn draw [self]
    (return)))
