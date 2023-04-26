from machine import Pin
from time import ticks_us, ticks_diff, sleep_us

bufsize = 32
timeout = 500000

class SingleLineDataTrans:
    def __init__(self, pin, bitus = 800, charus = 1500, rxbuf=32):
        self._pin = pin
        self._rx_init()
        self._rb = bytearray(rxbuf)
        bufsize = rxbuf
        self._rbt, self._tb = bytearray(1), bytearray(1)
        self._bitus, self._charus = bitus, charus
        self._bcnt = 0
        self._head, self._tail = 0, 0
        self._T1, self._T2, self._DT, self._Rdt = 0, 0, 0, 0
        self._irq = self._pin.irq()

    def _rx_init(self):
        self._pin.init(Pin.IN, pull=Pin.PULL_UP)
        self._irq = self._pin.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler = self._rxb)

    def _tx_init(self):
        self._pin.init(Pin.OUT, value = 1)
        self._irq = self._pin.irq(handler = None)

    def _wbit(self, d):
        if d & 0x80:
            sleep_us(self._bitus*2)
        else:
            sleep_us(self._bitus//2)
        self._pin(not self._pin())

    def write(self, buf):
        self._tx_init()
        for i in range(len(buf)):
            self._tb[0] = ord(buf[i]) if type(buf) is str else buf[i]
            self._pin(not self._pin())
            sleep_us(self._bitus)
            self._pin(not self._pin())
            for j in range(8):
                self._wbit(self._tb[0]<<j)
            sleep_us(self._charus)
        self._rx_init()
        return len(buf)

    def any(self):
        return (self._tail - self._head) % bufsize

    def _rxb(self, dummy):
        self._T2 = ticks_us()
        self._DT = ticks_diff(self._T2, self._T1)
        if  self._DT > timeout:
            self._bcnt = 1
        else:
            self._bcnt += 1
            if self._bcnt < 3:
                self._Rdt = self._DT
            else:
                self._rbt[0] <<= 1
                if self._DT > self._Rdt:
                    self._rbt[0] += 1
                if self._bcnt > 9:
                    self._bcnt = 0
                    self._rb[self._tail] = self._rbt[0]
                    self._tail = (self._tail + 1) % bufsize
                    if self._tail == self._head:
                        self._head = (self._head + 1) % bufsize
        self._T1 = self._T2

    def read(self, nbytes=bufsize):
        if self.any() == 0:
            return
        n = min(self.any(), nbytes)
        buf = bytearray(n)
        n = self.readinto(buf)
        return buf

    def readinto(self, buf, nbytes = None):
        if self.any() == 0:
            return 0
        if nbytes == None:
            nbytes = len(buf)
        n = min(self.any(), nbytes)
        for i in range(n):
            buf[i] = self._rb[(self._head + i) % bufsize]
        self._head = (self._head + n) % bufsize
        return n
                
