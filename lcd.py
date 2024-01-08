import time
from rpi_lcd import LCD

class LCDDisplay:
    def __init__(self, i2c_addr=0x27, cols=16, rows=2):
        self.lcd = LCD()
#        self.lcd.begin(cols, rows)

    def display_text(self, line1, line2):
        self.lcd.clear()
        self.lcd.text(line1,1)
        self.lcd.text(line2,2)
    def display_on_row(self, line, row):
        self.lcd.text(line,row)

