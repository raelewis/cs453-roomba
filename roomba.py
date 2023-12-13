# Rachel Lewis 
# CS Project
# Fall 2023
# This file serves as the main project file. It contains the primary functionality for the Roomba commands.

import serial, time
from datetime import datetime
import pandas as pd

"""This file serves as the main control / command hub for the roomba."""

class Roomba():
    def __init__(self):
        self.baudrate = 115200
        self.ser = None
        self.port = '/dev/tty.usbserial-DA017W4Z'
        self.valid_commands = {
            "START": 128,
            "SAFE": 131,
            "POWER": 133,
            "DRIVE": 137,
            "LEDS": 139,
            "SONG": 140,
            "PLAY": 141,
            "SENSORS": 142,
        }
        self.premade_songs = {
            # Simple scales
            0: [58, 64, 59, 64, 60, 64],
            1: [60, 64, 59, 64, 58, 64],

            # Mario Invincibility pt 1 and 2. Total length: 1.5 sec
            2: [72, 12, 72, 12, 72, 12, 62, 6, 72, 6, 0, 6, 72, 6, 0, 6, 62, 6,
                 72, 6, 62, 6, 72, 12],
            3: [71, 12, 71, 12, 71, 12, 60, 6, 71, 6, 0, 6, 71, 6, 0, 6, 60, 6,
                 71, 6, 60, 6, 71, 12]     
        }
        self.sensor_data = []               # Will store a list of dictionaries. This will then output into a csv file containing all sensor data.

    def _open_port(self):
        self.ser = serial.Serial(self.port, baudrate=self.baudrate, timeout=5)

    def _close_port(self):
        self.ser.close()

    def _send_cmd(self, cmd):
        """Function writes the command to the roomba. cmd must be a list."""
        print("Sending: ", cmd)
        for x in range(0,len(cmd)):
            cmd[x] = int(cmd[x])
        self.ser.write(bytes(cmd))

    def _read_cmd(self):
        """Function reads bytes from the roomba."""
        data = self.ser.read(26)
        return data

    """Roomba OpCode Commands"""
    def _start(self):
        """ Starts the SCI. The Start command must be sent before any
            other SCI commands. This command puts the SCI in passive
            mode.

            Serial sequence: [128]"""
        cmd = [self.valid_commands['START']]
        self._send_cmd(cmd)

    def _safe(self):
        """ This command puts the SCI in safe mode. The SCI must be in
            full mode to accept this command.
            Note: In order to go from passive mode to safe mode, use the Control
            command.

            Serial sequence: [131]"""
        cmd = [self.valid_commands['SAFE']]
        self._send_cmd(cmd)

    def _power(self):
        """Puts Roomba to sleep, the same as a normal “power” button
            press. The Device Detect line must be held low for 500 ms to
            wake up Roomba from sleep. The SCI must be in safe or full
            mode to accept this command. This command puts the SCI in
            passive mode.

            Serial sequence: [133]"""
        cmd = [self.valid_commands['POWER']]
        self._send_cmd(cmd)

    def _leds(self, led):
        """ Controls Roomba’s LEDs. The state of each of the spot, clean,
            max, and dirt detect LEDs is specified by one bit in the first data
            byte. The color of the status LED is specified by two bits in the
            first data byte. The power LED is specified by two data bytes, one
            for the color and one for the intensity. 

            Serial sequence: [139] [Led Bits] [Power Color] [Power Intensity]"""
        cmd = [self.valid_commands['LEDS']]
        for x in led:
            cmd.append(x)
        self._send_cmd(cmd)

    def _song(self, song_num, length, song):
        """ Specifies a song to the SCI to be played later. Each song is
            associated with a song number which the Play command uses
            to select the song to play. Users can specify up to 16 songs
            with up to 16 notes per song. 

            Serial sequence: [140] [Song Number] [Song Length] [NoteNumber 1] 
            [Note Duration 1] [Note Number 2] [Note Duration 2] etc."""
        
        cmd = [self.valid_commands['SONG'], song_num, length]
        for x in song:
            cmd.append(x)
        self._send_cmd(cmd)

    def _play(self, song_num):
        """ Plays one of 16 songs, as specified by an earlier Song
            command. If the requested song has not been specified yet,
            the Play command does nothing.

            Serial sequence: [141] [Song Number]"""
        
        cmd = [self.valid_commands['PLAY'], song_num]
        self._send_cmd(cmd)

    def _drive(self, velocity_high, velocity_low, radius_high, radius_low):
        """Controls Roomba’s drive wheels.

            Serial sequence: [137] [Velocity high byte] [Velocity low byte]
            [Radius high byte] [Radius low byte]"""
        
        cmd = [self.valid_commands['DRIVE'], velocity_high, velocity_low, radius_high, radius_low]
        self._send_cmd(cmd)

    def _sensors(self, packet):
        """Requests the SCI to send a packet of sensor data bytes. The
            user can select one of four different sensor packets. The sensor
            data packets are explained in more detail in the next section.
            The SCI must be in passive, safe, or full mode to accept this
            command. This command does not change the mode.
            
            Serial sequence: [142] [Packet Code]"""

        cmd = [self.valid_commands['SENSORS'], packet]
        self._send_cmd(cmd)
        return self._read_cmd()

    """Helper Functions""" 
    def _get_timestamp(self):
        now = datetime.now()
        return now.strftime("%m/%d/%Y, %H:%M:%S")
    
    def _to_csv(self):
        df = pd.DataFrame(self.sensor_data)
        df.to_csv("sensor_data.csv", index=False)
    
    def _move_from_danger(self):
        """WIP function attempting to use the data pulled from the sensor command to stop an unsafe drive."""
        self.drive(-200, 0)
        time.sleep(1)
        self.drive(0, 0)

    def _tohex(self, val):
        return hex((val + (1 << 16)) % (1 << 16))
    
    def _fromhex(self, val):
        s = val[2:]
        if len(s) < 4:
            zeros = 4-len(s)
            z=""
            for x in range(0, zeros):
                z = "0"+z
            s = z+s
        high = int(s[:2], 16)
        low = int(s[2:], 16)
        return high, low
    
    def _confirm_input(self, min_val, max_val, item):
        """Helper function to make sure user input is correct."""
        input_str = "Enter value for " + item + " [" + str(min_val) + "-" + str(max_val) + "]: "
        while True:
            val = input(input_str)
            if int(val) < int(min_val) or int(val) > int(max_val):
                continue
            else: 
                return int(val)

    """Sensor Unpack Functions"""
    def packet_zero(self, packet, packet_info):
        """Packet will return all sensor data."""
        first = packet[:10]
        second = packet[10:16]
        third = packet[16:]

        packet_info.update(self.packet_one(first, packet_info))
        packet_info.update(self.packet_two(second, packet_info))
        packet_info.update(self.packet_three(third, packet_info))
        self.sensor_data.append(packet_info)

    def packet_one(self, packet, packet_info):
        """Packet will return Bumps Wheeldrops, Wall, Cliff, Virtual Wall, Motor Overcurrents, Dirt Detector"""
        packet_info["Bumps Wheeldrops"] = packet[0]
        packet_info["Wall"] = packet[1]
        if packet[1] == 1:
            self._move_from_danger()
        packet_info["Cliff Left"] = packet[2]
        packet_info["Cliff Front Left"] = packet[3]
        if packet[3] == 1:
            self._move_from_danger()
        packet_info["Cliff Front Right"] = packet[4]
        if packet[4] == 1:
            self._move_from_danger()
        packet_info["Cliff Right"] = packet[5]
        packet_info["Virtual Wall"] = packet[6]
        packet_info["Motor Overcurrents"] = packet[7]
        packet_info["Dirt Detector Left"] = packet[8]
        packet_info["Dirt Detector Right"] = packet[9]
        return packet_info

    def packet_two(self, packet, packet_info):
        """Packet will return RCC, Buttons, Distance, Angle, Charging State"""
        packet_info["Remote Control Command"] = packet[0]
        packet_info["Buttons"] = packet[1]
        packet_info["Distance"] = int.from_bytes(packet[2:4])
        packet_info["Angle"] = int.from_bytes(packet[4:])
        return packet_info

    def packet_three(self, packet, packet_info):
        """Packet will return Voltage, Current, Temperature, Charge, Capacity"""
        packet_info["Charging State"] = packet[0]
        packet_info["Voltage"] = int.from_bytes(packet[1:3])
        packet_info["Current"] = int.from_bytes(packet[3:5])
        packet_info["Temperature"] = packet[5]
        packet_info["Charge"] = int.from_bytes(packet[6:8])
        packet_info["Capacity"] = int.from_bytes(packet[8:])
        return packet_info

    """Command Building Functions"""
    def _select_lights(self):
        """Allows the user to generate led data for the roomba to display."""
        dirt_detect = self._confirm_input(0, 1, "Dirt Detect LED")
        spot = self._confirm_input(0, 1, "Spot LED")
        clean = self._confirm_input(0, 1, "Clean LED")
        max_bit = self._confirm_input(0, 1, "Max LED")
        status_ops = ["00", "01", "10", "11"]
        input_str = """Enter value for Status\nOptions: [00 = off, 01 = red, 10 = green, 11 = amber]: """
        while True:
            status = input(input_str)
            if status not in status_ops:
                continue
            else: 
                break
        str_bit = "00" + str(status) + str(spot) + str(clean) + str(max_bit) + str(dirt_detect)
        led = int(str_bit, 2)
        return led
    
    def _generate_leds(self):
        """Allows the user to specify the LED light/intensity of the roomba."""
        led_bits = self._select_lights()
        power_color = self._confirm_input(0, 255, "Power Color")
        power_intensity = self._confirm_input(0, 255, "Power Intensity")
        return [led_bits, power_color, power_intensity]
    
    def _generate_song(self, song_num=None):
        """Allows the user to generate song data for the roomba to play."""
        max_length = 15
        song, notes, lens = [], [], []
        for x in range(0, max_length):
            notes.append(self._confirm_input(31, 127, "Note"))
            lens.append(self._confirm_input(0, 255, "Note Duration"))
            
            # If the user's song is less than the maximum length, exit.
            cont = input("Finished? yes/no: ")
            if cont == "yes":
                break

        for x in range(0, len(notes)):
            song.append(notes[x])
            song.append(lens[x])

        if song_num is None:
            song_num = self._confirm_input(0, 15, "Song Number")

        self._song(song_num, len(notes), song)

    """User Functions"""
    def start_roomba(self):
        self._open_port()
        self._start()
        self._safe()
        time.sleep(1)

    def stop_roomba(self):
        self._power()
        self._to_csv()

    def submit_song(self, song_num=None, song=None):
        """Allows a user to submit song data. If the song is None, generate song data."""
        if song:
            length = int(len(song)/2)
            if length == 0:
                length = 1
            self._song(song_num, length, song)
        else:
            self._generate_song(song_num)

    def submit_led(self, led=None):
        """Allows a user to submit led data. If the led cmd is None, generate led data."""
        if led:
            self._leds(led)
        else:
            led = self._generate_leds()
            self._leds(led)

    def play_song(self, song_num):
        """Allows the user to play the song number passed."""
        self._play(song_num)
    
    def select_song(self):
        """Allows the user to select a song to play a song saved to the roomba."""
        song_num = self._confirm_input(0, 15, "Song Number")
        self._play(song_num)

    def select_premade_song(self, song_num):
        """Allows the user to select a premade song to play. If the user does not pass a song number to this method, they will be prompted
        to select one from a list of options."""
        if song_num is None:
            song_num = self._confirm_input(0, len(self.premade_songs)-1, "Premade Song Number")
        length = int(len(self.premade_songs[song_num])/2)
        song = self.premade_songs[song_num]
        self._song(song_num, length, song)

    def select_sensors(self, packet=None):
        """Allows the user to select sensor data packet. If the user does not pass a packet number to this method, they will be prompted
        to select one from a list of options."""
        if packet is None:
            packet_ops = ["0", "1", "2", "3"]
            one_str = "1: Bumps Wheeldrops, Wall, Cliff, Virtual Wall, Motor Overcurrents, Dirt Detector\n"
            two_str = "2: RCC, Buttons, Distance, Angle, Charging State\n"
            three_str = "3: Voltage, Current, Temperature, Charge, Capacity\n"
            input_str = "Select a Packet:\n" + "0: All sensor data\n" + one_str + two_str + three_str
            packet = ""
            while True:
                packet = input(input_str)
                if packet not in packet_ops:
                    continue
                else: 
                    break
            packet = int(packet)
        data = bytearray(self._sensors(int(packet)))

        columns = ["Bumps Wheeldrops", "Wall", "Cliff Left", "Cliff Front Left", "Cliff Front Right", "Cliff Right", "Virtual Wall",
                    "Motor Overcurrents", "Dirt Detector Left", "Dirt Detector Right", "Remote Control Command", "Buttons", "Distance",
                    "Angle", "Charging State", "Voltage", "Current", "Temperature", "Charge", "Capacity"]
        packet_info = dict.fromkeys(columns, None)
        packet_info['timestamp'] = self._get_timestamp()
        
        if packet == 0:
            self.packet_zero(data, packet_info)
        elif packet == 1:
            packet_info = self.packet_one(data, packet_info)
            self.sensor_data.append(packet_info)
        elif packet == 2:
            packet_info = self.packet_two(data, packet_info) 
            self.sensor_data.append(packet_info) 
        else:
            packet_info = self.packet_three(data, packet_info)
            self.sensor_data.append(packet_info)  

    def drive(self, velocity=None, radius=None):
        """Allows the user to issue a command to the roomba based on text input."""
        
        if velocity is None:
            velocity = self._confirm_input("-500", "500", "Velocity in mm/s")
        if radius is None:
            radius = self._confirm_input("-2000", "2000", "Radius in mm/s")

        vel_hex = self._tohex(velocity)
        rad_hex = self._tohex(radius)
        velocity_high, velocity_low = self._fromhex(vel_hex)
        radius_high, radius_low = self._fromhex(rad_hex)
        self._drive(velocity_high, velocity_low, radius_high, radius_low)       