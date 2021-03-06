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
from PIL import Image, ImageDraw

import threading

SLICES=4

CHUNK = 32 # Size of each 'frame' in rolling buffer
FFT_LEN = CHUNK*20 # size of rolling buffer for FFT
RATE = 16000 # Sampling rate
SIGNAL_SCALE = .005 # Scaling factor for output

class Visualizer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.im = Image.new('1', (width, height), 255)
        self.signal = empty(FFT_LEN, dtype=int16)
        self.listen = threading.Thread(target=self.gather_audio)
        self.draw = threading.Thread(target=self.draw_waveform)

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

    def draw_waveform(self, display):
        start_time = dt.datetime.today().timestamp()
        while 1:
            # Now transform!
            try:
                fftspec = list(log(abs(x) * SIGNAL_SCALE) + 2 for x in rfft(self.signal)[:self.height])
            except ValueError:
                fftspec = [0] * SLICES

            #create an image
            img = Image.new('1', (self.width, self.height), 255)
            draw = ImageDraw.Draw(img)
            points = [val for pair in zip(range(self.width), fftspec) for val in pair]
            draw.line(points, 0)
            self.im = img.transpose(Image.FLIP_TOP_BOTTOM)

    def start(self):
        self.listen.start()
        self.draw.start()
