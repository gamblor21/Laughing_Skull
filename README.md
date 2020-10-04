# Light Sensitive Laughing Skull
![Laughing Skull](/hallowing.png)

Create a fun prank for Halloween or any time of the year. Hide the project somewhere dark and wait. When someone opens a door or shines a light on the proejct wakes up displaying an animated laughing skull and playing evil laughter. These last until it gets dark again (or they find the battery)

## Recommended Hardware

This project is written in CircuitPython and has been tested on several Adafruit boards and is easily adaptable to run on other hardware. It runs best on a M4 processor but can run acceptable on an nRF52840. The code has switches to turn off audio or animation, and to change the animation speed slower. All of which may help on a slower processor. The images are scaled for a 240x240 display but could be resized. The audio is mono and should play through any mono speaker.

Of the boards I have tested it on the project works best on the Hallowing M4. This amazing board has everything you need already built into it. The screen, light sensor and audio are all already there so nothing besides a small speaker is required.

A small battery is perfect to place this project somewhere dark and wait for an unsuspecting person to open the door.

## Tested Adafruit Hardware:
* [Hallowing M4](https://www.adafruit.com/product/4300)
* [Circuit Playground Bluefruit](https://www.adafruit.com/product/4333) with [TFT Gizmo](https://www.adafruit.com/product/4367)
* [Clue](https://www.adafruit.com/product/4500) with [PAM8302 Amplifier](https://www.adafruit.com/product/2130)
* [ItsyBitsy M4](https://www.adafruit.com/product/3800) with [PAM8320 Amplifier](https://www.adafruit.com/product/2130), [ST7789 240x240 display](https://www.adafruit.com/product/3787) and [ALS-PT19 Light Sensor](https://www.adafruit.com/product/2748)

All the projects had a small 4-8ohm speaker attached for audio out.

### The project requires the following components:
* Processor board to run the project (M4 recommended)
* 240x240 Display
* Audio out
* Light sensor

It is fairly easy to swap out components if you have another you would like to use. All initializations are at the top of the code.

## Configuration
The configuration is all near the top of the python file. These are the most likely values you will want to change.

```python
LIGHT_VALUE = 1500      # value at which we turn on / off the laughing
MODE_SWITCH_TIME = 0.2  # how long to wait for a changed reading
                        # to be consistent to change modes
LAUGHING_SPEED = 0.1   # how fast the animation runs

USE_AUDIO = True        # if you want to disable audio
USE_ANIMATION = True   # if you want to disable animation
```

## Ideas
This project could be expanded upon to change how it reacts in even more ways. 
* Boards like the Hallowing have a built in motion sensor that could be used (if you shake it maybe it says to put it down!)
* NeoPixels could light up in certain situations or to add to the surprise
* A microphone sensor could allow the project to react to sound instead of light
* New sounds an animations can be added following the base code that is provided


### Credits for Audio
The audio was a mix of several tracks from:
* [The Baron - Evil Laugh](https://freesound.org/people/The%20Baron/sounds/98382/)
* [TChild - Evil Laugh](https://freesound.org/people/tchild/sounds/319766/)
* [Craigh Smith - Women Screaming](https://freesound.org/people/craigsmith/sounds/438420/)
