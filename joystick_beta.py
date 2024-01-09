from gpiozero import MCP3008
import time

class Joystick:
    def __init__(self, channel_x=1, channel_y=2, channel_sw=0):
        self.x_axis = MCP3008(channel=channel_x)
        self.y_axis = MCP3008(channel=channel_y)
        self.switch = MCP3008(channel=channel_sw)

    def read_values(self):
        x_value = self.x_axis.value
        y_value = self.y_axis.value
        sw_value = self.switch.value
        return x_value, y_value, sw_value

joystick = Joystick()
#while True:
 #   x,y,z = joystick.read_values()
  #  print(x,y,z)
   # time.sleep(1)
