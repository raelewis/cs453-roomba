# Rachel Lewis 
# CS Project
# Fall 2023
# Testing LEDs. This demo will change the center leds to different colors and intensities.

import time
from roomba import Roomba

roomba = Roomba()
roomba.start_roomba()
time.sleep(1)
roomba.submit_led([25, 0, 128])
time.sleep(1)
roomba.submit_led([63, 255, 255])
time.sleep(1)
roomba.submit_led([47, 128, 128])
time.sleep(1)
roomba.submit_led([10, 64, 255])
time.sleep(1)
roomba.submit_led([53, 0, 255])
time.sleep(1)
roomba.submit_led([0, 0, 0])