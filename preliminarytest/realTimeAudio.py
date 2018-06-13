#!/usr/bin/env python
# encoding: utf-8

## Module infomation ###
# Python (3.4.4)
# numpy (1.10.2)
# PyAudio (0.2.9)
# matplotlib (1.5.1)
# All 32bit edition
########################

import numpy as np
import pyaudio
import time
import matplotlib.pyplot as plt
import madmom
from madmom.features.beats import RNNBeatProcessor, DBNBeatTrackingProcessor
from madmom.models import BEATS_LSTM
import collections
import librosa




class SpectrumAnalyzer:
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 512
    START = 0
    N = 512

    wave_x = 0
    wave_y = 0
    spec_x = 0
    spec_y = 0
    data = []

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.c_count = 0
        using_callback = True
        self.buffer = collections.deque(maxlen = self.RATE * 8)
        self.rnn = RNNBeatProcessor(online = True, nn_files=[BEATS_LSTM[0]])
        self.act_proc = DBNBeatTrackingProcessor(fps=100)
        if using_callback:
            self.stream = self.pa.open(format = self.FORMAT,
                channels = self.CHANNELS, 
                rate = self.RATE, 
                input = True,
                output = True,
                frames_per_buffer = self.CHUNK,
                stream_callback=self.callback)
            self.t_start = time.time()
            while self.stream.is_active():
                if len(self.buffer) == self.RATE * 8:
                    print('8 sec')
                    tmp = np.array(self.buffer) * 5
                    print(time.time() - self.t_start)
                    #tmp2 = self.rnn(tmp)
                    tmp2 = librosa.onset.onset_strength(tmp,sr=self.RATE, max_size=1,aggregate=np.median, n_mels=256)
                    t_axes = librosa.frames_to_time(np.arange(len(tmp2)),sr=self.RATE)
                    print(time.time() - self.t_start)
                    #self.rnn(self.buffer)
                    #tmp3 = self.act_proc(tmp2)
                    #print(tmp3)
                    tmp3_1,tmp3_2 = librosa.beat.beat_track(onset_envelope=tmp2, sr=self.RATE)
                    print('tempo is %f'% tmp3_1)
                    print('beat is ', t_axes[tmp3_2])
                    self.buffer.clear()
                    print(time.time() - self.t_start)

                time.sleep(0.01)

        else:
            self.stream = self.pa.open(format = self.FORMAT,
                channels = self.CHANNELS, 
                rate = self.RATE, 
                input = True,
                output = True,
                frames_per_buffer = self.CHUNK)
            self.t_start = time.time()
            self.loop()

    def callback(self,in_data, frame_count, time_info, status):
        self.data=np.fromstring(in_data, np.float32)
        for d in self.data:
            self.buffer.append(d)
        #print(self.data.shape)
        '''
        print(self.c_count * float(self.CHUNK) / self.RATE)
        print(time.time() - self.t_start)
        self.c_count +=1
        '''
        self.fft()
        #self.graphplot()
        return (in_data, pyaudio.paContinue)

    def loop(self):
        try:
            while True :
                self.data = self.audioinput()
                self.fft()
                #self.graphplot()

        except KeyboardInterrupt:
            self.pa.close()

        print("End...")

    def audioinput(self):

        ret = self.stream.read(self.CHUNK)
        ret = np.fromstring(ret, np.float32)
        '''
        print(self.c_count * float(self.CHUNK) / self.RATE)
        print(time.time() - self.t_start)
        '''
        self.c_count +=1
        return ret

    def fft(self):
        self.wave_x = range(self.START, self.START + self.N)
        self.wave_y = self.data[self.START:self.START + self.N]
        self.spec_x = np.fft.fftfreq(self.N, d = 1.0 / self.RATE)  
        y = np.fft.fft(self.data[self.START:self.START + self.N])    
        self.spec_y = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in y]

    def graphplot(self):
        plt.clf()
        # wave
        plt.subplot(311)
        plt.plot(self.wave_x, self.wave_y)
        plt.axis([self.START, self.START + self.N, -0.5, 0.5])
        plt.xlabel("time [sample]")
        plt.ylabel("amplitude")
        #Spectrum
        plt.subplot(312)
        plt.plot(self.spec_x, self.spec_y, marker= 'o', linestyle='-')
        plt.axis([0, self.RATE / 2, 0, 50])
        plt.xlabel("frequency [Hz]")
        plt.ylabel("amplitude spectrum")
        #Pause
        plt.pause(.01)

if __name__ == "__main__":
    spec = SpectrumAnalyzer()