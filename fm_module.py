import smbus as smbus
import subprocess
import curses
import curses.textpad
import time
from lcd import LCDDisplay
from db_radio import FMRadioFavorites
import RPi.GPIO as GPIO
from joystick_beta import Joystick
from decimal import Decimal, getcontext

i2c = smbus.SMBus(1)
i2c_address = 0x60
muted = False

def get_signal_strength(address):
    try:
        time.sleep(1)

        status_data = i2c.read_i2c_block_data(address, 0, 5)

        # Introduce a delay after reading the status register
        #time.sleep(0.5)

        # Extract the relevant bits for signal strength
        signal_strength = (status_data[3] & 0XF0) >> 4
        return signal_strength
    except IOError:
        subprocess.call(['i2cdetect', '-y', '1'])
        return None

def search_stations(address, start_freq, end_freq, step=0.1):
    for freq in range(int(start_freq * 10), int(end_freq * 10), int(step * 10)):
        freq = freq / 10.0  # Convert back to float
        set_freq(address, freq)
        strength = get_signal_strength(address)
        if strength > 6:
            set_freq(address, freq)
            break
    return freq

def init_radio(address):
    i2c.write_quick(address)
    time.sleep(0.1)


def set_freq(address, freq):

    freq14bit = int (4 * (freq * 1000000 + 225000) / 32768) # Frequency distribution for two bytes (according to the data sheet)
    freqH = freq14bit>>8
    freqL = freq14bit & 0xFF

    data = [0 for i in range(4)] # Descriptions of individual bits in a byte - viz.  catalog sheets
    init = freqH # freqH # 1.bajt (MUTE bit; Frequency H)
    data[0] = freqL # 2.bajt (frequency L)
    data[1] = 0xB0 #0b10110000 # 3.bajt (SUD; SSL1, SSL2; HLSI, MS, MR, ML; SWP1)
    data[2] = 0x10 #0b00010000 # 4.bajt (SWP2; STBY, BL; XTAL; smut; HCC, SNC, SI)
    data[3] = 0x00 #0b00000000 # 5.bajt (PLREFF; DTC; 0; 0; 0; 0; 0; 0)
    try:
      i2c.write_i2c_block_data (address, init, data) # Setting a new frequency to the circuit
      print("Frequency set to: " + str(freq))
      # Wait for the module to settle before proceeding
      time.sleep(0.1)
      # Get and display signal strength
      signal_strength =str(get_signal_strength(i2c_address))
      lcd_display.display_text(str(freq), signal_strength)
      i2c.write_i2c_block_data (address, init, data)
    except IOError:
      subprocess.call(['i2cdetect', '-y', '1'])


def mute(address):
    global muted
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
        muted = True
    except IOError:
        subprocess.call(['i2cdetect', '-y', '1'])

def control_frequency(address, controller, db, freq):
    global muted, curr_fav
    x,y,sw = controller.read_values()
    change = False
    print(freq)
    if(freq>107.9):
        freq=87.5
    if(x<0.1 and y>0.94 and len(db.get_favorite_frequencies())>0):
        if(curr_fav==0):
            curr_fav=len(db.get_favorite_frequencies())-1
        else:
            curr_fav-=1
        freq = db.get_favorite_frequencies()[curr_fav][0]
        change = True
        time.sleep(2)
    elif(x>0.94 and y>0.95 and len(db.get_favorite_frequencies())>0):
        if(curr_fav==len(db.get_favorite_frequencies())-1):
            curr_fav=0
        else:
            curr_fav+=1
        freq = db.get_favorite_frequencies()[curr_fav][0]
        change = True
        time.sleep(2)
    elif(x<0.1):
        freq =round(freq-0.1,1)
        change = True
        time.sleep(1)
    elif(x>0.99):
        freq =round(freq+0.1,2)
        change = True
        time.sleep(1)
    elif(y<0.1):
        freq = search_stations(address, freq+0.2, 107.9)
    #elif(y>0.99):
        #freq = search_stations(address, freq-0.2, 100.0)
        #change = True
    if(sw<0.5 and not muted):
        mute(address)
        time.sleep(1)
    elif(sw<0.5 and muted):
        set_freq(address, freq)
        muted = False
    if not GPIO.input(4) and (freq not in db_controler.get_favorite_frequencies()):
        db_controler.add_frequency_to_database(freq)
        lcd_display.display_on_row("Added to fav",1);
        time.sleep(1.5)
        lcd_display.display_on_row(str(freq),1)
    if not GPIO.input(17):
        db_controler.delete_frequency_from_database(freq)
        lcd_display.display_on_row(str(freq)+"DELETED",1)
        time.sleep(1.5)
        lcd_display.display_on_row(str(freq),1)
    if(change):
        set_freq(address, freq)
    time.sleep(1)
    return freq

if __name__ == '__main__':
    init_radio(i2c_address)
    frequency = 100.9 # sample starting frequency
    curr_fav = 0
    lcd_display = LCDDisplay()
    db_controler = FMRadioFavorites()
    joystick = Joystick()
    set_freq(i2c_address,frequency)
    try:
        while True:
            frequency = control_frequency(i2c_address, joystick, db_controler, frequency)
    except KeyboardInterrupt:
        mute(i2c_address)
