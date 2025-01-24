(import casino)
(import spritekit :as sk)
(import asyncio)

(asyncio.run 
  ((fn :async []
     (let [casino (casino.Casino)]
       (await (casino.connect))
       (with [window (sk.window)]
         (for [dt (window.loop)]
           (for [event window.poll]
             (print event))))
       (await (casino.close))))))
