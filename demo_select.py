# Rachel Lewis 
# CS Project
# Fall 2023
# Loop Test

import time
from roomba import Roomba

roomba = Roomba()
roomba.start_roomba()

while True:
    user_input = int(input("Available options: 0: LED, 1: SONG, 2: PLAY, 3: DRIVE, 4: SENSOR, 5: POWER\n"))
    if user_input == 0:
        roomba.submit_led()
    elif user_input == 1:
        roomba.submit_song()
    elif user_input == 2:
        roomba.select_song()
    elif user_input == 3:
        roomba.drive()
    elif user_input == 4:
        roomba.select_sensors()
    elif user_input == 5:
        roomba.stop_roomba()
        break
    time.sleep(2)