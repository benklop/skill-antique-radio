"""
User mode device driver for Noritake GU7000-series Vacuum Fluorescent Displays.
Modified to allow more flexible control

Copyright (c) 2020 benklop@gmail.com
Copyright (c) 2006 spacemarmot@users.sourceforge.net

This file is released under the GNU Lesser General Public Licence.
See the file LICENSE for details.
"""

from PIL import Image
from bitarray import bitarray
import time
from visualizer import Visualizer

BS  = b'\x08'
HT  = b'\x09'
LF  = b'\x0A'
HOM = b'\x0B'
CR  = b'\x0D'
CLR = b'\x0C'

#____ abstract base class ______________________________________________________

class GU7000(object):

    def __init__(self, W, H):

        self.W = W
        self.H = H

    def showCursor(self, show=1):

        self.write(b'\x1f\x43%c' % show)

    def setCursor(self, x, y):

        self.write(b'\x1F\x24%c%c%c%c' % (int(x%256), int(x/256), int(y%256), int(y/256)))

    def clearDisplay(self):

        self.write(CLR)

    def initDisplay(self):

        self.write(b'\x1B\x40')

    def setWriteMixMode(self, mode):

        self.write(b'\x1f\x77%c' % mode)

    def setBrightness(self, brightness):

        self.write(b'\x1f\x58%c' % brightness)

    def displayBitImage(self, w, h, image):

        args = ( int(w%256), int(w/256), int(h%256), int(h/256), image)
        self.write(b'\x1f\x28\x66\x11%c%c%c%c\x01%s' % args)

    def reverseDisplay(self, reverse=True):

        self.write(b'\x1f\x72%c' % reverse)

    def displayImage(self, image):
        data = bitarray()
        for i in range(image.width):
            for j in range(image.height):
                if image.getpixel((i, j)) == 255:
                    data.append(False)
                else:
                    data.append(True)
        self.displayBitImage(image.width, image.height / 8, data.tobytes())

    def displayImageFile(self, image_file):
        self.displayImage(Image.open(image_file))


#____ serial ___________________________________________________________________

try:

    import serial # http://pyserial.sourceforge.net

    class GU7000Ser(GU7000):

        def __init__(self, W, H, dev='/dev/ttyS4'):

            GU7000.__init__(self, W, H)
            self._ser = serial.Serial(dev, baudrate=38400, writeTimeout=1)
            self._ser.close()
            self._ser.open()

        def write(self, data):

            _ser.write(data)

except: print('GU7000 serial not available')

class VFDisplay(GU7000Ser):

    def __init__(self):
        self.d = GU7000Ser(140, 16, dev='/dev/ttyS4')
        self.d.clearDisplay()
        time.sleep(1)
        self.d.setCursor(0,0)
        self.vis = Visualizer(d)
        self.vis.start()

    def splashScreen():
        for i in range(0,10):
            d.setBrightness(i)
            d.displayImageFile('images/anim/westinghouse00.bmp')

        for i in range(32):
            d.displayImageFile('images/anim/westinghouse' + str(i).zfill(2) + '.bmp')

        time.sleep(2)
        for i in range(10,0,-1):
            d.setBrightness(i)
            d.displayImageFile('images/anim/westinghouse31.bmp')

        d.clearDisplay()
        d.setBrightness(5)

    def startVis():
        while 1:
            display.displayImage(vis.im)


if __name__ == '__main__':
    display = VFDisplay()
    display.splashScreen()
    display.startVis()
