import smbus as smbus 
import subprocess
import curses
import curses.textpad
import time
from lcd import LCDDisplay
from db_radio import FMRadioFavorites
import RPi.GPIO as GPIO

i2c = smbus.SMBus(1) # newer version RASP (512 megabytes)
i2c_address = 0x60

def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    stdscr.timeout(100)  # Set a timeout to make getch non-blocking
    return stdscr

def get_signal_strength(address):
    """read signal strength from TEA5767"""
    try:
        # Introduce a delay before reading the status register
        time.sleep(0.1)

        # Read the Status register
        status_data = i2c.read_i2c_block_data(address, 0, 5)

        # Introduce a delay after reading the status register
        time.sleep(0.5)

        # Extract the relevant bits for signal strength
        signal_strength = (status_data[2] >> 4) & 0x0F

        return signal_strength
    except IOError:
        subprocess.call(['i2cdetect', '-y', '1'])
        return None

def search_stations(address, start_freq, end_freq, step=0.1):
    """Search for radio stations between start_freq and end_freq."""
    for freq in range(int(start_freq * 10), int(end_freq * 10), int(step * 10)):
        freq = freq / 10.0  # Convert back to float
        set_freq(address, freq)
        strength = get_signal_strength(address)
        time.sleep(0.5)
        if strength > 3:
            break
    return freq

def init_radio(address):
    """initialize hardware"""
    i2c.write_quick(address)
    time.sleep(0.1)


def set_freq(address, freq):
    """set Radio to specific frequency"""
    freq14bit = int (4 * (freq * 1000000 + 225000) / 32768) # Frequency distribution for two bytes (according to the data sheet)
    freqH = freq14bit>>8 #int (freq14bit / 256)
    freqL = freq14bit & 0xFF

    data = [0 for i in range(4)] # Descriptions of individual bits in a byte - viz.  catalog sheets
    init = freqH # freqH # 1.bajt (MUTE bit; Frequency H)  // MUTE is 0x80
    data[0] = freqL # 2.bajt (frequency L)
    data[1] = 0xB0 #0b10110000 # 3.bajt (SUD; SSL1, SSL2; HLSI, MS, MR, ML; SWP1)
    data[2] = 0x10 #0b00010000 # 4.bajt (SWP2; STBY, BL; XTAL; smut; HCC, SNC, SI)
    data[3] = 0x00 #0b00000000 # 5.bajt (PLREFF; DTC; 0; 0; 0; 0; 0; 0)
    try:
      i2c.write_i2c_block_data (address, init, data) # Setting a new frequency to the circuit
      print("Frequency set to: " + str(freq))
      # Wait for the module to settle before proceeding
      time.sleep(0.3)
      # Get and display signal strength
      signal_strength =str(get_signal_strength(i2c_address))
      lcd_display.display_text(str(freq), signal_strength)
      i2c.write_i2c_block_data (address, init, data)
    except IOError:
      subprocess.call(['i2cdetect', '-y', '1'])


def mute(address):
    """"mute radio"""
    freq14bit = int(4 * (0 * 1000000 + 225000) / 32768)
    freqL = freq14bit & 0xFF
    data = [0 for i in range(4)]
    init = 0x80
    data[0] = freqL
    data[1] = 0xB0
    data[2] = 0x10
    data[3] = 0x00
    try:
        i2c.write_i2c_block_data(address, init, data)
        lcd_display.display_text("Radio Muted","")
    except IOError:
        subprocess.call(['i2cdetect', '-y', '1'])


if __name__ == '__main__':
    init_radio(i2c_address)
    frequency = 100.1 # sample starting frequency
    # terminal user input infinite loop
    stdscr = init_curses()
    curses.noecho()
    lcd_display = LCDDisplay()
    db_controler = FMRadioFavorites()

    while True:
        c = stdscr.getch()

        if not GPIO.input(4):
            if frequency in db_controler.get_favorite_frequencies():
                continue
            db_controler.add_frequency_to_database(frequency)
            lcd_display.display_on_row("Added to fav",1);
            time.sleep(1.5)
            lcd_display.display_on_row(str(frequency),1)
        if not GPIO.input(17):
            db_controler.delete_frequency_from_database(frequency)
            time.sleep(1.5)
            print(db_controler.get_favorite_frequencies())


        if c == ord('g'):
            frequency = search_stations(i2c_address, frequency+0.2, 108.0)
            set_freq(i2c_address, frequency)
            time.sleep(1)
        if c == ord('f'): # set to 101.1
            frequency = 101.1
            set_freq(i2c_address, frequency)
            time.sleep(1)
        elif c == ord('v'): # set to 102.1
            frequency = 102.1
            set_freq(i2c_address, frequency)
            time.sleep(1)
        elif c == ord('w'): # increment by 1
            frequency += 1
            set_freq(i2c_address, frequency)
            time.sleep(1)
        elif c == ord('s'): # decrement by 1
            frequency -= 1
            set_freq(i2c_address, frequency)
            time.sleep(1)
        elif c == ord('e'): # increment by 0.1
            frequency += 0.1
            set_freq(i2c_address, frequency)
            time.sleep(1)
        elif c == ord('d'): # decrement by 0.1
            frequency -= 0.1
            set_freq(i2c_address, frequency)
            time.sleep(1)
        elif c == ord('m'): # mute
            mute(i2c_address)
            time.sleep(1)
        elif c == ord('u'): # unmute
            set_freq(i2c_address, frequency)
            time.sleep(1)
        elif c == ord('q'): # exit script and cleanup
            mute(i2c_address)
            curses.endwin()
            break
