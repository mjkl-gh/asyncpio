#!/usr/bin/env python

import asyncio

import asyncpio

class decoder:

   """
   A class to read Wiegand codes of an arbitrary length.

   The code length and value are returned.

   EXAMPLE

   #!/usr/bin/env python

   import asyncio

   import asyncpio

   import wiegand

   def callback(bits, value):
      print("bits={} value={}".format(bits, value))

   pi = asyncpio.pi()
   await pi.connect()

   w = await decoder.create(pi, 14, 15, callback)

   await asyncio.sleep(300)

   await w.cancel()

   await pi.stop()
   """

   def __init__(self, pi, gpio_0, gpio_1, callback, bit_timeout=5):

      """
      Instantiate with the pi, gpio for 0 (green wire), the gpio for 1
      (white wire), the callback function, and the bit timeout in
      milliseconds which indicates the end of a code.

      The callback is passed the code length in bits and the value.
      """

      self.pi = pi
      self.gpio_0 = gpio_0
      self.gpio_1 = gpio_1

      self.callback = callback

      self.bit_timeout = bit_timeout

      self.in_code = False

   @classmethod
   async def create(cls, pi, gpio_0, gpio_1, callback, bit_timeout=5):
      self = cls(pi, gpio_0, gpio_1, callback, bit_timeout=bit_timeout)

      await self.pi.set_mode(gpio_0, asyncpio.INPUT)
      await self.pi.set_mode(gpio_1, asyncpio.INPUT)

      await self.pi.set_pull_up_down(gpio_0, asyncpio.PUD_UP)
      await self.pi.set_pull_up_down(gpio_1, asyncpio.PUD_UP)

      await self.cb_0 = self.pi.callback(gpio_0, asyncpio.FALLING_EDGE, self._cb)
      await self.cb_1 = self.pi.callback(gpio_1, asyncpio.FALLING_EDGE, self._cb)

   async def _cb(self, gpio, level, tick):

      """
      Accumulate bits until both gpios 0 and 1 timeout.
      """

      if level < asyncpio.TIMEOUT:

         if self.in_code == False:
            self.bits = 1
            self.num = 0

            self.in_code = True
            self.code_timeout = 0
            await self.pi.set_watchdog(self.gpio_0, self.bit_timeout)
            await self.pi.set_watchdog(self.gpio_1, self.bit_timeout)
         else:
            self.bits += 1
            self.num = self.num << 1

         if gpio == self.gpio_0:
            self.code_timeout = self.code_timeout & 2 # clear gpio 0 timeout
         else:
            self.code_timeout = self.code_timeout & 1 # clear gpio 1 timeout
            self.num = self.num | 1

      else:

         if self.in_code:

            if gpio == self.gpio_0:
               self.code_timeout = self.code_timeout | 1 # timeout gpio 0
            else:
               self.code_timeout = self.code_timeout | 2 # timeout gpio 1

            if self.code_timeout == 3: # both gpios timed out
               await self.pi.set_watchdog(self.gpio_0, 0)
               await self.pi.set_watchdog(self.gpio_1, 0)
               self.in_code = False
               self.callback(self.bits, self.num)

   async def cancel(self):

      """
      Cancel the Wiegand decoder.
      """

      await self.cb_0.cancel()
      await self.cb_1.cancel()


async def main():
   def callback(bits, value):
      print("bits={} value={}".format(bits, value))

   pi = asyncpio.pi()
   await pi.connect()

   w = await decoder.create(pi, 14, 15, callback)

   await asyncio.sleep(300)

   await w.cancel()

   await pi.stop()


if __name__ == "__main__":
   asyncio.run(main())

