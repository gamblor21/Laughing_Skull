import board
import displayio
import digitalio
import analogio
import adafruit_imageload
import time
import neopixel
from adafruit_led_animation.animation.pulse import Pulse
import supervisor
import busio
import adafruit_us100
from audiomp3 import MP3Decoder
try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!

# configuration
USE_LIGHT_SENSOR = False # if you want to disable the light sensor
USE_DISTANCE_SENSOR = True # if you want to disable the distance sesnor
USE_NEOPIXELS = True # if you want to use the onboard neopixels

LIGHT_VALUE = 1500      # value at which we turn on / off the laughing
DISTANCE_VALUE = 50      # value at which we turn on / off the laughing
MODE_SWITCH_TIME = 0.2  # how long to wait for a changed reading
                        # to be consistent to change modes
LAUGHING_SPEED = 0.1   # how fast the animation runs

USE_AUDIO = True        # if you want to disable audio
USE_ANIMATION = True   # if you want to disable animation

if USE_DISTANCE_SENSOR is True:
    uart = busio.UART(board.TX, board.RX, baudrate=9600)
    us100 = adafruit_us100.US100(uart)

# initialize on board neopixels
pixels = neopixel.NeoPixel(board.NEOPIXEL, 4, brightness=1.0, auto_write=False)
pixels.fill((0,0,0))
pixels.show()
pulse = Pulse(pixels, speed=0.3, color=(250,0,0))

# turn the board LED off so it does not affect our light sensor
supervisor.set_rgb_status_brightness(0)

# Light sensor to know when to turn on
light = analogio.AnalogIn(board.LIGHT)

# speaker enable if the board supports it
speaker_enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
speaker_enable.direction = digitalio.Direction.OUTPUT
speaker_enable.value = True

# Set up audio
audio = AudioOut(board.SPEAKER)
mp3 = open("laugh.mp3", "rb")
decoder = MP3Decoder(mp3)

# set up the display for the board or external
display = board.DISPLAY
display.brightness = 0.0 # start off

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

    if USE_LIGHT_SENSOR is True:
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

    if USE_DISTANCE_SENSOR is True:
        distance = us100.distance

        if distance <= DISTANCE_VALUE:
            if mode is "laughing" and switching_to_mode is "waiting":
                switch_timer = 0
                switching_to_mode = ""
            if mode is "waiting":
                if switch_timer == 0:
                    switch_timer = time.monotonic()
                    switching_to_mode = "laughing"
                if switching_to_mode is "laughing" and (time.monotonic() - switch_timer) > MODE_SWITCH_TIME:
                    print("Switch mode on distance to laughing: ", distance)
                    switch_timer = 0
                    switching_to_mode = ""
                    mode = "laughing"
                    new_mode = True

        # large distance
        elif distance > DISTANCE_VALUE:
            if mode is "waiting" and switching_to_mode is "laughing":
                switch_timer = 0
                switching_to_mode = ""
            if mode is "laughing":
                if switch_timer == 0:
                    switch_timer = time.monotonic()
                    switching_to_mode = "waiting"
                if switching_to_mode is "waiting" and (time.monotonic() - switch_timer) > MODE_SWITCH_TIME:
                    print("Switch mode on distance to waiting: ", distance)
                    mode = "waiting"
                    new_mode = True
                    switch_timer = 0

    if mode is "waiting":
        if new_mode is True:
            display.brightness = 0
            if USE_AUDIO is True:
                audio.stop()
            display.refresh()
            if USE_NEOPIXELS:
                pixels.fill((1,1,2))
                pixels.show()
                pulse.reset()
            new_mode = False

    if mode is "laughing":
        if new_mode is True:
            display.brightness = 1.0
            if USE_AUDIO is True:
                audio.play(decoder, loop=True)
            display.refresh()
            if USE_NEOPIXELS:
                # if you want to set the neopixels to do a static
                # display when turned on put it here
                #pixels.fill((250,0,0))
                #pixels.show()
                pass
            new_mode = False

        pulse.animate()

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