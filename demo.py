# Rachel Lewis 
# CS 453 Project
# Fall 2023
# This demo tests each command created in the Roomba class. It plays the Mario Invincibility theme.
# While playing the song, the roomba will drive in a circle and change the center led lights.

import time
from roomba import Roomba

roomba = Roomba()
roomba.start_roomba()

# Play the top notes for Mario's Invincibility: https://musescore.com/xiaomigros/invincible-smb
measure_one = [72, 12, 72, 12, 72, 12, 62, 6, 72, 6, 0, 6, 72, 6, 0, 6, 62, 6, 72, 6, 62, 6, 72, 12]
measure_two = [71, 12, 71, 12, 71, 12, 60, 6, 71, 6, 0, 6, 71, 6, 0, 6, 60, 6, 71, 6, 60, 6, 71, 12] 
roomba.submit_song(2, measure_one)
roomba.submit_song(3, measure_two)
roomba.select_sensors(0)

# Loop through the song a few times.
roomba.drive(200, 300)          # Spin in place counterclockwise
for x in range(0, 3):
    roomba.play_song(2)
    roomba.select_sensors(0)
    roomba.submit_led([63, 0, 255])
    time.sleep(1.55)
    roomba.play_song(3)
    roomba.select_sensors(0)
    roomba.submit_led([63, 255, 255])
    time.sleep(1.55)
roomba.submit_led([0, 0, 0])
roomba.select_sensors(0)
roomba.drive(0, 0)
roomba.select_sensors(0)
roomba.stop_roomba()