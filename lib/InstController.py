'''The realtime controller of SC instrument
'''
import FoxDot

from FoxDot.lib import *
from FoxDot.lib.SCLang.SynthDef import SynthDef, SynthDefBaseClass, FileSynthDef


class InstController():

    def __init__(self, timbre, degree=None, **kwargs):
        self.player = Player()
        self.parameters = {}
        self.degree = degree
        self.timbre = timbre
        for key, value in kwargs.items():
            self.parameters[key] = value

        if isinstance(timbre, SCLang.SynthDef):
            self.player >> timbre(degree, **kwargs)
        elif isinstance(timbre, FileSynthDef):
            self.player >> timbre(degree, **kwargs)
        else:
            
            print('SynthdefNotfFound')
            return

    def change_degree(self, new_degree):
        self.degree = new_degree
        #self.player.stop()
        self.player >> self.timbre(new_degree,**self.parameters)

    def change_parameters(self, **kwargs):
        for key, value in kwargs.items():
            self.parameters[key] = value

    def stop(self):
        self.player.stop()

    def play(self):
        self.player.play()

    def follow(self,follow_inst):
        self.player >> self.timbre(**follow_inst.parameters).follow(follow_inst.player)
        self.degree = follow_inst.degree
        self.parameters = follow_inst.parameters
        return self

    def __add__(self, data):
        self.player >> self.timbre(self.degree,**self.parameters) + data
        return self
    ''' Operands Err for subtracting a list or a pattern
    def __sub__(self, data):
        self.player >> self.timbre(self.degree,**self.parameters) - data
    '''

if __name__ == '__main__':
    import time
    import numpy as np
    time.sleep(1)
    #p1 >> space([(0, 2, 4)])
    tone_p = FoxDot.lib.var([0,4,5,3], 4)
    drum1 = play("")
    bass1  = InstController(FoxDot.bass,tone_p, dur=PDur(3,8), amp =P[0.8] | P[0.6].stutter(2))
    pads1 = InstController(FoxDot.pads,tone_p + (0,2), dur=PDur(7,16), amp =P[0.7] | P[0.4].stutter(6))
    test1 = InstController(pluck, P[0,4,5,3], dur=[4], amp = 0.5)
    test2 = InstController(space, P[0,4,5,3], dur=[4]).follow(test1)
    #print(type(test1),type(test2))
    #test2.follow(test1)
    test2 += (0,2,4)
    #test1.play()
    Clock.every(16,lambda: d1 >> play("(x[--])xu[--]", sample=2))
    while(1):
        #print(int(Clock.now()),tone_p)
        time.sleep(1)
