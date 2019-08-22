
from PIL import Image, ImageDraw
import sys
import numpy as np
import SWHear
from gu7000 import GU7000Ser as Display

class AudioVisualiser:
    def __init__(self):

        self.im = Image.new(1, (140, 16))
        self.draw = ImageDraw.Draw(self.im)
        self.maxFFT=0
        self.maxPCM=0
        self.ear = SWHear.SWHear(rate=44100,updatesPerSecond=20)
        self.ear.stream_start()
        self.d = Display(140, 16, dev='/dev/ttyS2')

    def update(self):
        if not self.ear.data is None and not self.ear.fft is None:
            #im = Image.new(1, (140, 16))
            #draw = ImageDraw.Draw(im)
            pcmMax=np.max(np.abs(self.ear.data))
            if pcmMax>self.maxPCM:
                self.maxPCM=pcmMax
            if np.max(self.ear.fft)>self.maxFFT:
                self.maxFFT=np.max(np.abs(self.ear.fft))
            self.draw.line((self.ear.fftx, self.ear.fft/self.maxFFT))
            self.d.displayImage(self.im)


if __name__=="__main__":
    av = AudioVisualiser()
    while True:
        av.update()
