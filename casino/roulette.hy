(import .croupier *)

(defclass Roulette [Croupier]
  (defn __init__ [self]
    (.__init__ (super)))
  
  (defn draw [self]
    (draw-text "roulette!!" 10 20 20 BLUE)))
