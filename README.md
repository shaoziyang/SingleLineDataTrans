# Single Line Data Transmision

https://github.com/shaoziyang/SingleLineDataTrans

Use any GPIO for single line data transmission between MCUs. 

```


         .---------.                .---------.
         |         |                |         |
         |         |                |         |
         |   GPIO8 o--------o-------o PA1     |
         |         |        |       |         |
         |         |        |       |         |
         |  ESP32  |        |       |  STM32  |
         |         |        |       |         |
         '---------'        |       '---------'
                            |
                            |       .---------.
                            |       |         |
                            |       |         |
                            '-------o IO5     |
                                    |         |
                                    | ESP8266 |
                                    |         |
                                    '---------'

```

Because many MCUs have fewer interfaces, it is not convenient to transmit data between them. Especially when using microsython, many devices do not support SPI/I2C slave mode, and the number of UARTs is very few, so transferring data between MCUs is subject to many limitations.

The **SingleLineDataTrans** library provides a very simple way to transfer data between MCUs, using only one GPIO and not occupying other resources such as timers, UARTs, external interrupts, etc.

## Theory

Each byte consists of 9 bits, with the first bit representing bitus and then 8 data bits (MSB).


```
bit      7  6   5  4 3 2 1  0
0x61     0  1   1  0 0 0 0  1
   ``|  |`|   |```| |`| |`|   |``````|
     |  | |   |   | | | | |   |      |
     |__| |___|   |_| |_| |___|      |_
    bitus                      charus
```

Due to differences in various systems, it is not possible to accurately predict the values of parameters. If the speed of the slave is fast enough, the bitus and charus parameters can be set smaller, otherwise the parameters needs to be set larger. When there is an error in receiving data, it is necessary to set the parameters larger.

For example, when using ESP32 as a slave to receive data, you may set *bitus=300* and *charus=600*; and when using ESP8266 as a slave to receive data, you may set *bitus=3500* and *charus=6500*.  


## Tested platform

- STM32
- ESP32
- ESP8266


## usage

The basic usage is similar to UART

```py
from SingleLineDataTrans import SingleLineDataTrans
from machine import Pin

sldt = SingleLineDataTrans(Pin(5))
sldt.write('123')
sldt.read()
```

## function

- **SingleLineDataTrans**(pin, bitus = 300, charus = 600, rxbuf=32)
    Define single line data transmission object:
    - pin, GPIO object for single line communication
    - bitus, basic time to send a bit of data (in milliseconds)
    - charus, delay time between two bytes (in milliseconds)
    - rxbuf, size of the data receive buffer
  
- **any**()
    Return the number of received data.

- **idle()**
    Check if the bus is in idle state, only sending data in idle state will not cause bus conflicts.
  
- **write**(buf)
    Send data. Return the number of bytes sent.
  
- **read**([nbytes])
    Read characters.
  
- **readinto**(buf, [nbytes])
    Read bytes into the buf.
  

