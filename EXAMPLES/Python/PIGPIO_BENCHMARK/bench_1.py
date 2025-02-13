#!/usr/bin/env python

#
# WARNING!
#

##############################################################################
#                                                                            #
# Unless you know what you are doing don't run this script with anything     #
# connected to the gpios.  You will CAUSE damage.                            #
#                                                                            #
##############################################################################

#
# WARNING!
#

import asyncio

import asyncpio

delay = 30

class gpioTest:

   def __init__(self, pi, gpio, edge, freq, duty):
      self.pi = pi
      self.gpio = gpio
      self.edge = edge
      self.freq = freq
      self.duty = duty
      self.calls = 0

   def cb(self, g, t, l):
      self.calls = self.calls + 1
      # print g,t,l

   def num(self):
      return self.calls

   async def start(self):
      await self.pi.set_PWM_frequency(self.gpio, self.freq)
      await self.pi.set_PWM_range(self.gpio, 25)
      await self.pi.set_PWM_dutycycle(self.gpio, self.duty)
      self.n = await self.pi.callback(self.gpio, self.edge, self.cb)

   async def stop(self):
      await self.pi.set_PWM_dutycycle(self.gpio, 0)
      await self.n.cancel()

async def main():
   pi = asyncpio.pi()
   await pi.connect()

   t1 =  gpioTest(pi, 4, asyncpio.EITHER_EDGE,  4000,  1)
   t2 =  gpioTest(pi, 7, asyncpio.RISING_EDGE,  8000,  2)
   t3 =  gpioTest(pi, 8, asyncpio.FALLING_EDGE, 8000,  3)
   t4 =  gpioTest(pi, 9, asyncpio.EITHER_EDGE,  4000,  4)
   t5 =  gpioTest(pi,10, asyncpio.RISING_EDGE,  8000,  5)
   t6 =  gpioTest(pi,11, asyncpio.FALLING_EDGE, 8000,  6)
   t7 =  gpioTest(pi,14, asyncpio.EITHER_EDGE,  4000,  7)
   t8 =  gpioTest(pi,15, asyncpio.RISING_EDGE,  8000,  8)
   t9 =  gpioTest(pi,17, asyncpio.FALLING_EDGE, 8000,  9)
   t10 = gpioTest(pi,18, asyncpio.EITHER_EDGE,  4000, 10)
   t11 = gpioTest(pi,22, asyncpio.RISING_EDGE,  8000, 11)
   t12 = gpioTest(pi,23, asyncpio.FALLING_EDGE, 8000, 12)
   t13 = gpioTest(pi,24, asyncpio.EITHER_EDGE,  4000, 13)
   t14 = gpioTest(pi,25, asyncpio.RISING_EDGE,  8000, 14)

   # R1: 0 1     4 7 8 9 10 11 14 15 17 18 21 22 23 24 25
   # R2:     2 3 4 7 8 9 10 11 14 15 17 18    22 23 24 25 27 28 29 30 31

   tests = [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14]

   for i in tests: await i.start()

   await asyncio.sleep(delay)

   for i in tests: await i.stop()

   await pi.stop()

   tot = 0
   msg = ""

   for i in tests:
      tot += i.num()
      msg += str(i.num()) + " "

   print(msg)

   print("eps={} ({}/{})".format(tot/delay, tot, delay))

asyncio.run(main())
