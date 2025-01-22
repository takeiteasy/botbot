(import pyray *)
(import asyncio)
(import .roulette *)

(defn :async run []
  (let [screen-width 800
        screen-height 600]
    (let [r (Roulette)]
      (print r.value))
    (init-window screen-width screen-height "test")
    (set-target-fps 60)
    (while (not (window-should-close))
      (begin-drawing)
      (clear-background RAYWHITE)
      (draw-text "hello!" 10 10 20 RED)
      (end-drawing))

    (close-window)))
