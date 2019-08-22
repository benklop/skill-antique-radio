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
SIGNAL_SCALE = .0005 # Scaling factor for output

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

    try:
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
                fftspec = list(log(abs(x) * SIGNAL_SCALE) + 2 for x in rfft(signal)[:WIDTH])
            except ValueError:
                fftspec = [0] * SLICES

            #create an image
            im = Image.new('1', (WIDTH, HEIGHT), 1)
            draw = ImageDraw.Draw(im)
            draw.line(zip(iter(fftspec), iter(range(WIDTH))), 0)
            d.displayImage(im)

            # Print it
            lines = [
                ''.join(spark(x - i+1, x) for x in fftspec)
                for i in range(HEIGHT / 8, 0, -1)
            ]
            sys.stdout.write('│' + '│\n│'.join(lines) + '│')
            sys.stdout.write('\033[' + str((HEIGHT / 8) - 1) +'A\r')
    except KeyboardInterrupt:
        sys.stdout.write('\n' * HEIGHT / 8)
    finally:
        # Turn the cursor back on
        sys.stdout.write('\033[?25h')

if __name__ == "__main__":
    run()
