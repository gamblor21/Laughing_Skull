# MIT License
#
# Copyright (c) 2020 Mark Komus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import board
import displayio
from adafruit_st7789 import ST7789
import digitalio
import analogio
import adafruit_imageload
import time
import supervisor
import pulseio
from audiomp3 import MP3Decoder
try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!

# configuration
LIGHT_VALUE = 1500      # value at which we turn on / off the laughing
MODE_SWITCH_TIME = 0.2  # how long to wait for a changed reading
                        # to be consistent to change modes
LAUGHING_SPEED = 0.1   # how fast the animation runs

USE_AUDIO = True        # if you want to disable audio
USE_ANIMATION = True   # if you want to disable animation

# turn the board neopixel off so it does not affect our light sensor
supervisor.set_rgb_status_brightness(0)

# Light sensor to know when to turn on
light = analogio.AnalogIn(board.A3)

# Set up audio
audio = AudioOut(board.A0)
mp3 = open("laugh.mp3", "rb")
decoder = MP3Decoder(mp3)

# set up the display for the board or external
displayio.release_displays()

spi = board.SPI()
tft_cs = board.D11
tft_dc = board.D9

display_bus = displayio.FourWire(
    spi, command=tft_dc, chip_select=tft_cs, reset=board.D10
)

display = ST7789(display_bus, width=240, height=240, rowstart=80)

display_brightness = digitalio.DigitalInOut(board.D7)
display_brightness.direction = digitalio.Direction.OUTPUT
display_brightness.value = False # start off

# load the images for the skull
bitmap_top, palette_top = adafruit_imageload.load("/skull_top.bmp",
                                        bitmap=displayio.Bitmap,
                                        palette=displayio.Palette)

bitmap_close, palette_close = adafruit_imageload.load("/skull_close.bmp",
                                        bitmap=displayio.Bitmap,
                                        palette=displayio.Palette)

bitmap_open, palette_open = adafruit_imageload.load("/skull_open.bmp",
                                        bitmap=displayio.Bitmap,
                                        palette=displayio.Palette)

bitmap_middle, palette_middle = adafruit_imageload.load("/skull_middle.bmp",
                                        bitmap=displayio.Bitmap,
                                        palette=displayio.Palette)

# Create the TileGrids for the skull picture
skull_top = displayio.TileGrid(bitmap_top, pixel_shader=palette_top)
skull_top.x = 53 # center on the display
skull_top.y = 10 # little down from the top

skull_close = displayio.TileGrid(bitmap_close, pixel_shader=palette_close)
skull_close.x = 61 # align with the top
skull_close.y=135

skull_open = displayio.TileGrid(bitmap_open, pixel_shader=palette_open)
skull_open.x = 61 # align with the top
skull_open.y=135

skull_middle = displayio.TileGrid(bitmap_middle, pixel_shader=palette_middle)
skull_middle.x = 62 # align with the top
skull_middle.y=135

# Create a Group to hold the TileGrids
group = displayio.Group()

# Add the skull top to the Group
group.append(skull_top)
group.append(skull_middle) # start with the mouth partly open

# Add the Group to the Display
display.show(group)

# Turn off auto_refresh to save on processing time on slower boards
display.auto_refresh=False
display.refresh()

mode = "waiting" # set mode to waiting or laughing
new_mode = True # set True if we have switched modes

# light values must change for enough time to remove bouncing
# where the light may on the border of a change
switch_timer = 0
switching_to_mode = ""

# animation counters
current_frame = 3
last_frame_time = 0

while True:
    lvalue = light.value # this can change rapidly so choose one value

    # high amount of light
    if lvalue >= LIGHT_VALUE:
        if mode is "laughing" and switching_to_mode is "waiting":
            switch_timer = 0
            switching_to_mode = ""
        if mode is "waiting":
            if switch_timer == 0:
                switch_timer = time.monotonic()
                switching_to_mode = "laughing"
            if switching_to_mode is "laughing" and (time.monotonic() - switch_timer) > MODE_SWITCH_TIME:
                print("Switch mode on light to laughing: ", lvalue)
                switch_timer = 0
                switching_to_mode = ""
                mode = "laughing"
                new_mode = True

    # low amount of light (dark)
    elif lvalue < LIGHT_VALUE:
        if mode is "waiting" and switching_to_mode is "laughing":
            switch_timer = 0
            switching_to_mode = ""
        if mode is "laughing":
            if switch_timer == 0:
                switch_timer = time.monotonic()
                switching_to_mode = "waiting"
            if switching_to_mode is "waiting" and (time.monotonic() - switch_timer) > MODE_SWITCH_TIME:
                print("Switch mode on light to waiting: ", light.value)
                mode = "waiting"
                new_mode = True
                switch_timer = 0

    if mode is "waiting":
        if new_mode is True:
            display_brightness.value = False
            if USE_AUDIO is True:
                audio.stop()
            display.refresh()
            new_mode = False

    if mode is "laughing":
        if new_mode is True:
            display_brightness.value = True
            if USE_AUDIO is True:
                audio.play(decoder, loop=True)
            display.refresh()
            new_mode = False

        # Make the skull laugh open/close once
        if USE_ANIMATION is True:
            if (time.monotonic() - last_frame_time) > LAUGHING_SPEED:
                current_frame = (current_frame + 1) % 4

                if current_frame is 0:
                    group.remove(skull_middle)
                    group.append(skull_close)
                elif current_frame is 1:
                    group.remove(skull_close)
                    group.append(skull_middle)
                elif current_frame is 2:
                    group.remove(skull_middle)
                    group.append(skull_open)
                elif current_frame is 3:
                    group.remove(skull_open)
                    group.append(skull_middle)

                display.refresh()
                last_frame_time = time.monotonic()