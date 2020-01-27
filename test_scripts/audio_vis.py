#!/usr/bin/env python3

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import pyaudio
import time
import datetime as dt
from math import log
from numpy.fft import rfft
from numpy import int16, empty, fromstring, roll
from gu7000 import GU7000Ser as display
from PIL import Image, ImageDraw

import threading

WIDTH=140
HEIGHT = 16
SLICES=4

CHUNK = 32 # Size of each 'frame' in rolling buffer
FFT_LEN = CHUNK*20 # size of rolling buffer for FFT
RATE = 16000 # Sampling rate
SIGNAL_SCALE = .005 # Scaling factor for output

class AudioVis:
    def __init__(self):
        self.im = Image.new('1', (WIDTH, HEIGHT), 255)
        self.signal = empty(FFT_LEN, dtype=int16)

    def get_data(self):
        try:
            data = stream.read(chunk)
        except IOError as ex:
            if ex[1] != pyaudio.paInputOverflowed:
                raise
            data = '\x00' * chunk
        data

    def gather_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1, # Mono
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        while 1:
            # Roll in new frame into buffer
            while stream.get_read_available() < CHUNK:
                time.sleep(0.000001)
            try:
                frame = stream.read(CHUNK, exception_on_overflow=False)
            except IOError as e:
                if e.args[1] != pyaudio.paInputOverflowed:
                    raise
                continue
            self.signal = roll(self.signal, -CHUNK)
            self.signal[-CHUNK:] = fromstring(frame, dtype=int16)
    
    def display_waveform(self):
        d = display(140, 16, dev='/dev/ttyS4')
        time.sleep(0.1)
        d.clearDisplay()
        time.sleep(0.1)
        d.setCursor(0, 0)
        start_time = dt.datetime.today().timestamp()
        i=0
        while 1:
            # Now transform!
            try:
                fftspec = list(log(abs(x) * SIGNAL_SCALE) + 2 for x in rfft(self.signal)[:WIDTH])
            except ValueError:
                fftspec = [0] * SLICES

            #create an image
            img = Image.new('1', (WIDTH, HEIGHT), 255)
            draw = ImageDraw.Draw(img)
            points = [val for pair in zip(range(WIDTH), fftspec) for val in pair]
            draw.line(points, 0)
            self.im = img.transpose(Image.FLIP_TOP_BOTTOM)
            
            d.displayImage(self.im)
            #time_diff = dt.datetime.today().timestamp() - start_time
            #i += 1
            #print(i / time_diff)
    def run(self):
        process = threading.Thread(target=self.gather_audio)
        process.start()
        disp = threading.Thread(target=self.display_waveform)
        disp.start()

if __name__ == "__main__":
    vis = AudioVis()
    vis.run()
