# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import pyaudio
from math import log
from numpy.fft import rfft
from numpy import int16, empty, fromstring, roll
from gu7000 import GU7000Ser as display
from PIL import Image, ImageDraw

import threading

WIDTH=140
HEIGHT = 16

SLICES=4

CHUNK = int(WIDTH / SLICES) # Size of each 'frame' in rolling buffer
FFT_LEN = CHUNK*20 # size of rolling buffer for FFT
RATE = 8000 # Sampling rate
SIGNAL_SCALE = .005 # Scaling factor for output

im = Image.new('1', (WIDTH, HEIGHT), 255)

def gather_audio():
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=1, # Mono
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )
    signal = empty(FFT_LEN, dtype=int16)

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
        img = Image.new('1', (WIDTH, HEIGHT), 255)
        draw = ImageDraw.Draw(img)
        points = [val for pair in zip(range(WIDTH), fftspec) for val in pair]
        draw.line(points, 0)
        print('writing image')
        im = img.transpose(Image.FLIP_TOP_BOTTOM)

def display_waveform():
    d = display(140, 16, dev='/dev/ttyS2')
    while 1:
        d.displayImage(im)

if __name__ == "__main__":
     process = threading.Thread(target=gather_audio)
     process.start()
     disp = threading.Thread(target=display_waveform)
     disp.start()
