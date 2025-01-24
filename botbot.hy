(import casino)
(import asyncio)
(import pyray *)

(asyncio.run 
  ((fn :async []
     (let [casino (casino.Casino)]
       (await (casino.connect))
       (init-window 640 480 "botbot")
       (set-target-fps 60)
       (while (not (window-should-close))
         (begin-drawing)
         (clear-background RAYWHITE)
         (draw-text "hello!" 10 10 20 RED)
         (end-drawing))
       (await (casino.close))))))
