# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import pyaudio
from math import log
from numpy.fft import rfft
from numpy import int16, empty, fromstring, roll
from gu7000 import GU7000Ser as display
from PIL import Image, ImageDraw

WIDTH=140
HEIGHT = 16

SLICES=4

CHUNK = int(WIDTH / SLICES) # Size of each 'frame' in rolling buffer
FFT_LEN = CHUNK*20 # size of rolling buffer for FFT
RATE = 8000 # Sampling rate
SIGNAL_SCALE = .005 # Scaling factor for output

SPARKS = [
  ' ',
  '\u2581',
  '\u2582',
  '\u2583',
  '\u2584',
  '\u2585',
  '\u2586',
  '\u2587',
  '\u2588'
]
SPARKS_LEN = len(SPARKS)


def spark(i, full):
    i = min(int(max(0.0, i) * SPARKS_LEN), SPARKS_LEN-1)
    if full > HEIGHT:
        return '\033[0;31m' + SPARKS[i] + '\033[0m'
    return SPARKS[i]

def run():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1, # Mono
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    signal = empty(FFT_LEN, dtype=int16)

    d = display(140, 16, dev='/dev/ttyS2')

    this_frame = 0
    # Disable cursor
    sys.stdout.write('\033[?25l')
    while 1:
        # Roll in new frame into buffer
        try:
            frame = stream.read(CHUNK)
        except IOError as e:
            if e[1] != pyaudio.paInputOverflowed:
                raise
            continue
        signal = roll(signal, -CHUNK)
        signal[-CHUNK:] = fromstring(frame, dtype=int16)

        # Now transform!
        try:
            fftspec = list(log(abs(x) * SIGNAL_SCALE) + 8 for x in rfft(signal)[:WIDTH])
        except ValueError:
            fftspec = [0] * SLICES

        this_frame = this_frame + 1
        #create an image
        im = Image.new('1', (WIDTH, HEIGHT), 255)
        draw = ImageDraw.Draw(im)
        points = [val for pair in zip(range(WIDTH), fftspec) for val in pair]
        draw.line(points, 0)
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
        if this_frame % 20 == 0:
            d.displayImage(im)

if __name__ == "__main__":
    run()
