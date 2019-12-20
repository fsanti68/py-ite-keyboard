#!/usr/bin/env python3.8

import sys, usb.core, usb.util, getopt, string
from colour import Color

class ITEKeyboard:
  __SETUP_COMMAND = [0x08, 0x02, 0x33, 0x00, 0x24, 0x00, 0x00, 0x00]

  __LIGHT_MODES = {
        'off': [0x08, 0x02, 0x03, 0x05, 0x00, 0x08, 0x01, 0x00],
        'fade': [0x08, 0x02, 0x02, 0x05, 0x32, 0x08, 0x00, 0x00],
        'wave': [0x08, 0x02, 0x03, 0x05, 0x32, 0x08, 0x00, 0x00],
        'dots': [0x08, 0x02, 0x04, 0x05, 0x32, 0x08, 0x00, 0x00],
        'rainbow': [0x08, 0x02, 0x05, 0x05, 0x32, 0x08, 0x00, 0x00],
        'explosion': [0x08, 0x02, 0x06, 0x05, 0x32, 0x08, 0x00, 0x00],
        'snake': [0x08, 0x02, 0x09, 0x05, 0x32, 0x08, 0x00, 0x00],
        'raindrops': [0x08, 0x02, 0x0a, 0x05, 0x32, 0x08, 0x00, 0x00]
    }

  def __init__(self):
    vid = 0x048d
    pid = 0xce00
    self.device = usb.core.find(idVendor=vid, idProduct=pid)
    if self.device is None:
      sys.exit("Keyboard ITE (%s,%s) not found." % (vid, pid))

    self.device_index, self.interface, self.endpoint = self.__get_device_index()

    try:
      if self.device.is_kernel_driver_active(self.device_index):
          self.device.detach_kernel_driver(self.device_index)
    except usb.core.USBError as e:
      sys.exit("Kernel driver won't give up control over device: %s" % str(e))

    if self.interface is None:
      sys.exit("Unable to get device and interface")

    self.state = ITEKeyboardState(self.device, self.endpoint)

  def __get_device_index(self):
    endpoint = None
    interface = None
    device_index = 0
    for cfg in self.device:
        for intf in cfg:
          for endp in intf:
                if usb.util.endpoint_direction(endp.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                  endpoint = endp
                  interface = intf
        device_index += 1
    return (device_index, interface, endpoint)

  def setup_keyboard(self):
    ret = self.device.ctrl_transfer(bmRequestType = 0x21, bRequest = 9,
                    wValue = 0x300, wIndex = 1, data_or_wLength = self.__SETUP_COMMAND)

  def set_mode(self, mode):
    ctrlbuf = self.__LIGHT_MODES.get(mode);
    self.device.ctrl_transfer(bmRequestType = 0x21, bRequest = 9,
                    wValue = 0x300, wIndex = 1, data_or_wLength = ctrlbuf)


class ITEKeyboardState:
  def __init__(self, device, endpoint):
    self.msg = [[0 for col in range(64)] for row in range(6)]
    self.device = device
    self.endpoint = endpoint

  def set_key_color(self, row, column, color):
    try:
      c = Color(color)
    except ValueError as e:
      sys.exit(str(e))

    if column < 0 or column > 20:
        sys.exit('Invalid column index: should be between 0 and 20')

    self.msg[row][column + 0] = int(c.blue * 255)
    self.msg[row][column + 21] = int(c.green * 255)
    self.msg[row][column + 42] = int(c.red * 255)

  def update(self):
    index = 0
    for index, m in enumerate(self.msg):
      ct = self.device.ctrl_transfer(0x21, 9, 0x300, 1, [0x16, 0, index, 0, 0, 0, 0, 0])
      wr = self.endpoint.write(m, 500)


def usage():
    prg_name = sys.argv[0].split('/').pop()
    spaces = ' ' * len(prg_name)
    print("usage: %s [cmd] [args]" % prg_name)
    print("where 'cmd' and 'args' can be:")
    print("  mode [off | fade | wave | dots | rainbow | explosion | snake | raindrops]")
    print("  color [rows range] [columns range] [color name]")
    print("\n\nColumn and row ranges can be expressed as:")
    print(" - single value:         3            row #3")
    print(" - list of values:       0,2,4        rows 0, 2 and 4")
    print(" - range of values:      5-17         columns from 5 to 17")
    print(" - mixed list and range: 0-2,17,18    columns 0, 1, 2, 17 and 18")
    print(" - all possible values:  all          rows from 0 to 5 and columns from 0 to 20")
    print("\n\nSome examples:")
    print("  # %s mode snake                         starts snake mode" % prg_name)
    print("  # %s color 0 all yellow                 yellow on row #0 keys" % prg_name)
    print("  # %s color 0,5 all red 2-4 all white    red on rows 0 and 5 and white on rows 2 to 4" % prg_name)
    print("  # %s color 1,4-5 0-1,18-19 blue         blue for the first and" % prg_name)
    print("    %s                                    last 2 keys of rows 1, 4 and 5" % spaces)

def getrange(s, max):
  r = list()
  lines = s.split(',')
  for line in lines:
    x = line.split('-')
    if len(x) == 1:
      if x[0] == 'all':
        for j in range(max + 1):
          r.append(j)
      else:
        r.append(int(x[0]))
    else:
      for j in range(int(x[0]), int(x[1]) + 1):
        r.append(j)
  return r


def main(argv):
  mode = None
  colors = None
  if len(argv) == 0:
    usage()
    sys.exit()

  for i in range(len(argv)):
    if argv[i] == '-h' or argv[i] == '--help':
      usage()
      sys.exit()

    elif argv[i] == "mode":
      mode = argv[i + 1].lower()
      dev = ITEKeyboard()
      dev.setup_keyboard()
      print('set mode to %s' % mode)
      dev.set_mode(mode)
      sys.exit()

    elif argv[i] == "color":
      dev = ITEKeyboard()
      dev.setup_keyboard()
      
      while i < len(argv) - 2:
        rows = getrange(argv[i + 1].lower(), 5)
        cols = getrange(argv[i + 2].lower(), 20)
        color = argv[i + 3]
        i += 3
        for row in rows:
          for col in cols:
            dev.state.set_key_color(row, col, color);
      dev.state.update()


if __name__ == "__main__":
  main(sys.argv[1:])