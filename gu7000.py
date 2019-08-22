"""
User mode device driver for Noritake GU7000-series Vacuum Fluorescent Displays.

Copyright (c) 2006 spacemarmot@users.sourceforge.net

This file is released under the GNU Lesser General Public Licence.
See the file LICENSE for details.
"""

BS  = '\x08'
HT  = '\x09'
LF  = '\x0A'
HOM = '\x0B'
CR  = '\x0D'
CLR = '\x0C'

#____ abstract base class ______________________________________________________

class GU7000(object):

    def __init__(self, W, H):

        self.W = W
        self.H = H

    def showCursor(self, show=1):

        self.write('\x1f\x43%c' % show)

    def setCursor(self, x, y):

        self.write('\x1F\x24%c%c%c%c' % (x%256, x/256, y%256, y/256))

    def clearDisplay(self):

        self.write(CLR)

    def initDisplay(self):

        self.write('\x1B\x40')

    def setWriteMixMode(self, mode):

        self.write('\x1f\x77%c' % mode)

    def setBrightness(self, brightness):

        self.write('\x1f\x58%c' % brightness)

    def displayBitImage(self, w, h, image):

        args = ( w%256, w/256, h%256, h/256, image)
        self.write('\x1f\x28\x66\x11%c%c%c%c\x01%s' % args)

    def reverseDisplay(self, reverse=True):

        self.write('\x1f\x72%c' % reverse)

    def displayImageFile(self, image_file):

        from PIL import Image
        from bitarray import bitarray

        data = bitarray()
        src = Image.open(image_file)
        for i in range(src.width):
            for j in range(src.height):
                if src.getpixel((i, j)) == 255:
                    data.append(False)
                else:
                    data.append(True)
        d.displayBitImage(140, 2, data.tobytes())

#____ serial ___________________________________________________________________

try:

    import serial # http://pyserial.sourceforge.net

    class GU7000Ser(GU7000):

        def __init__(self, W, H, dev='/dev/ttyS2'):

            GU7000.__init__(self, W, H)
            self._ser = serial.Serial(dev, baudrate=38400, writeTimeout=1)
            self._ser.close()
            self._ser.open()

        def write(self, data):

            self._ser.write(data)

except: print 'GU7000 serial not available'

if __name__ == '__main__':

    import time

    d = GU7000Ser(140, 16, dev='/dev/ttyS2')

    d.clearDisplay()
    time.sleep(1)
    d.setCursor(0,0)

    for i in range(1,9):
        d.setBrightness(i)
        d.displayImageFile('images/anim/westinghouse00.bmp')

    for i in range(32):
        d.displayImageFile('images/anim/westinghouse' + str(i).zfill(2) + '.bmp')



