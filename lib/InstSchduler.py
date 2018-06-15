'''
Scheduler
Used for the controling the music event on time

'''

import threading
import sched
import time
import FoxDot
import numpy as np
import os
import matplotlib.pyplot as plt
import yaml
from mir_eval.chord import encode_many as chord_encode
from scipy import signal

from loop_event import EventPipeline
from tool.midi2p import midi2P, midinote2degree
from tool.midi2tracks import TrackSet
from tool.drawtool import draw_function

tone_interval = [0, 0.5, 1, 1.5, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6]


def degree_add(deg, dist):
    degree = deg % 7
    tmp_dist = tone_interval.index(degree) + dist
    if tmp_dist < 0:
        return tone_interval[tmp_dist] - 7 + deg // 7 * 7
    elif tmp_dist > 11:
        return tone_interval[tmp_dist - 12] + 7 + deg // 7 * 7
    return tone_interval[tmp_dist] + deg // 7 * 7


class InstScheduler():

    def __init__(self, FoxDot_clock, source_path):
        self.s = sched.scheduler(time.time, time.sleep)
        self.fclock = FoxDot_clock
        self.Inst_dict = {}
        self.player_dict = {}
        self.parameters = {}
        self.playing_flag = {}
        self.need_prepare = 0
        self.pipeline = EventPipeline()
        self.pipeline.Processor(self.EventProcessor, self.fclock_now)
        self.source_path = source_path

    def __getitem__(self, Inst_name):
        return self.Inst_dict[Inst_name]

    def __str__(self):
        out_str = 'Current Registerd Inst:\n\n'
        out_str += str(self.Inst_dict.keys())
        return out_str

    def AddInst(self, Inst_name, Instcontrol, **kwargs):
        '''
        Note: Automatically overwrite
        '''
        self.Inst_dict[Inst_name] = Instcontrol
        p = {}
        for key, value in kwargs.items():
            p[key] = value
        self.parameters[Inst_name] = p
        self.parameters[Inst_name]['tunable'] = False
        if 'tune_instrument' in self.meta:
            if Inst_name in self.meta['tune_instrument']:
                self.parameters[Inst_name]['tunable'] = True

        if Inst_name not in self.player_dict:
            self.player_dict[Inst_name] = FoxDot.lib.Player()
        self.playing_flag[Inst_name] = False

    def PlayInst(self, Inst_name):
        self.player_dict[Inst_name] >> self.Inst_dict[
            Inst_name](**self.parameters[Inst_name])
        self.playing_flag[Inst_name] = True

    def fclock_now(self):
        if self.period:
            return self.fclock.now() / 16 % self.period
        else:
            return self.fclock.now() / 16

    def AddMidi(self, Inst_name, port_num):
        Patterns = midi2P(file_path, None, verb=0)
        Patterns[0]['MidiNum'] = port_num  # may have some bugs?
        self.AddInst(Inst_name, FoxDot.lib.MidiOut, **Patterns[0])

    def AddMidiFolder(self, style_name):
        self.style_name = style_name
        folder_path = os.path.join(self.source_path, self.style_name)

        tracks = TrackSet(folder_path)
        wrap_path = os.path.join(folder_path, 'SC_Abelton.txt')
        tracks.wrapping(wrap_path)
        self.loadmeta()
        for n, p in zip(tracks.tracks_name, tracks.tracks_set):
            self.AddInst(n, FoxDot.lib.MidiOut, **p[0])

    def loadmeta(self):
        f = open(os.path.join(self.source_path, 'meta.yaml'))
        self.meta = yaml.load(f)[self.style_name]
        if 'bar_per_loop' in self.meta and 'beat_per_bar' in self.meta:
            self.set_tempo_pattern(
                self.meta['beat_per_bar'], self.meta['bar_per_loop'])

    def chord2degree(chord):
        root, bitmap, _ = chord_encode(chord)
        true_bitmap = np.roll(bitmap, root)
        midinote, _ = np.where(true_bitmap)
        return [midinote2degree(n) for n in midinote]

    def chord_distance(self, chord_patterns):
        org, _, _ = chord_encode(self.meta['chord_seq'])
        target, _, _ = chord_encode(chord_patterns)
        return target - org

    def ChordOverride(self, chord_dist):
        '''
        * Not all the instruments can be tuned
        * We need to find thw bar in the midi objects (by start_time attribute?)
        '''

        # Check if the input chord_pattern is compatible to the loop rythm
        if len(chord_pattern) != self.bar_loop:
            raise(
                'The input chord is not compatible with the set tempo pattern. Please check it.')
        # c_degree = self.chord_distance(chord_pattern)
        start_anchor = np.arange(
            self.bar_loop + 1).astype(np.float32) * self.beat_bar


        for key, value in self.parameters.items():
            if value['tunable']:

                bar_notes = [[value['degree'][i] for i, t in enumerate(
                    value['start_time']) if a0 <= t and t < a1] for a0, a1 in zip(start_anchor[:-1], start_anchor[1:])]
                new_deg = []

                for g_list in  bar_notes:
                    # return an array of notes represented in degree
                    new_deg += [tuple([degree_add(n, chord_dist)for n in g])
                                for g in g_list]
                self.change_parameters(key, degree=new_deg)

        return

    def change_parameters(self, Inst_name, **kwargs):
        for key, value in kwargs.items():
            self.parameters[Inst_name][key] = value
        if self.playing_flag[Inst_name]:
            self.PlayInst(Inst_name)

    def StopInst(self, Inst_name):
        self.player_dict[Inst_name].stop()
        self.playing_flag[Inst_name] = False

    def EventProcessor(self, event_type, event_arg):
        '''
        Read-In and pipeline
        '''

        '''
        Action
        '''

        if hasattr(event_type, '__iter__') == False:
            event_type = [event_type]
        if hasattr(event_arg, '__iter__') == False:
            event_type = [event_arg]
        for e, arg in zip(event_type, event_arg):
            if e == 'Play':
                if arg['Inst_name'] not in self.Inst_dict:
                    self.AddInst(**arg)
                self.PlayInst(Inst_name=arg['Inst_name'])
            elif e == 'Stop':
                self.StopInst(Inst_name=arg['Inst_name'])
            elif e == 'ChangeParameter':
                self.change_parameters(**arg)
            elif e == 'Gen_Live':
                self.live_generator(**arg)
            elif e == 'Loop_End':
                print('Loop_end')
                self.pipeline.sent_request()
            else:
                print('Event type Wrong!')

        return

    def Ordered_event(self):
        self.pipeline.event_clear()
        for i, k in enumerate(self.Inst_dict.keys()):
            self.pipeline.PushEvent(['Play'], [{'Inst_name': k}], i)
        return

    def Random_event(self, period_bar):
        self.pipeline.event_clear()
        perm_key = np.random.permutation(list(self.Inst_dict.keys()))
        for i, k in enumerate(perm_key):
            self.pipeline.PushEvent(
                ['Play'], [{'Inst_name': k}], i * period_bar)

    def live_generator(self, prev_pros, pros, event_time):
        '''
        Real-time generating the instrument playing event.
        need to perform with some rule to generate a better result
        '''
        delt_pros = pros - prev_pros

        if delt_pros > 0:
            inst_play = [key for key,
                         value in self.playing_flag.items() if not value]
            method = ['Play'] * int(delt_pros)
            new_evet = np.random.choice(
                inst_play, int(delt_pros), replace=False)
            args = [{'Inst_name': n} for n in new_evet]
            print(method[0], args)
            self.pipeline.InsertEvent(
                method, args, event_time, vol=True)
            return
        if delt_pros < 0:
            inst_play = [key for key,
                         value in self.playing_flag.items() if value]
            method = ['Stop'] * int(-delt_pros)
            new_evet = np.random.choice(
                inst_play, int(-delt_pros), replace=False)
            args = [{'Inst_name': n} for n in new_evet]
            print(['Stop'], args)
            self.pipeline.InsertEvent(
                method, args, event_time, vol=True)
            return

    def Live_event(self):
        '''
        Define a prosperity function which can limit the current number of playing Instruments
        **** Not implemented well Now ****
        '''
        self.pipeline.event_clear()
        self.need_prepare = 1
        num_level = min(10, len(self.Inst_dict))
        num_point = 5
        min_pos = 0.2
        max_pos = 1
        self.canvas_width = 500
        self.canvas_height = 300
        self.bd = 20
        y_max = self.canvas_height - self.bd
        y_min = self.bd
        canvs = draw_function(self.canvas_width, self.canvas_height, self.bd)
        raw_data = np.array(canvs.data).T
        flip_y = y_max - raw_data[1]

        quant_y = np.minimum(
            np.round(flip_y / y_max * num_level + 2), num_level)
        loop_y = np.concatenate([quant_y, np.flip(quant_y, 0)])

        # determine a proper period
        self.period = num_level * 4

        resample_y = np.round(signal.resample(loop_y, self.period))
        '''
        plt.plot(resample_y)
        plt.title('prosperity function')
        plt.show()
        '''
        prev_pros = 0
        # generate live random event
        for p, b in zip(resample_y, range(self.period)):
            if p != prev_pros:
                self.pipeline.PushEvent(
                    ["Gen_Live"], [{'prev_pros': prev_pros, 'pros': p, 'event_time': b}], b - 1)
            prev_pros = p
        self.pipeline.PushEvent(
            ["Loop_End"], [{'is_loop': True}], self.period - 1)

    def set_tempo_pattern(self, beat_bar=4, bar_loop=4):
        self.beat_bar = beat_bar
        self.bar_loop = bar_loop

    def CheckingAsyLoop(self):
        '''
        Asynchronous main loop for checking the event online
        '''
        #self.play_bpm = self.fclock.bpm = play_bpm
        self.fclock.set_time(0.1)
        cont = self.pipeline.sent_request()
        self.fclock.set_time(-0.1)

        self.start_time = time.time()
        loop_dur = self.beat_bar * self.bar_loop * (60. / self.fclock.bpm)
        sleep_time = loop_dur / 2.
        while(cont):
            cont = self.pipeline.sent_request(0)
        while(1):

            time_take = loop_dur - ((time.time() - self.start_time) % loop_dur)
            self.s.enter(time_take, 1, self.pipeline.sent_request, (0,))
            cont = self.s.run()
            while(cont):
                cont = self.pipeline.sent_request(0)

        return

    def StartInTime(self, delay_time, play_bpm):
        '''
        Start the event pipeline after delay_time directly
        '''
        self.sent_time = time.time()
        if self.need_prepare:
            self.fclock.set_time(-16)
            cont = self.pipeline.sent_request(0)
            while(cont):
                cont = self.pipeline.sent_request(0)
        #self.start_time = time.time()
        self.fclock.set_time(-0.1)
        self.play_bpm = self.fclock.bpm = play_bpm
        loop_thread = threading.Timer(
            delay_time - 60. / play_bpm * 1, self.CheckingAsyLoop, ())
        loop_thread.daemon = True
        loop_thread.start()

        return


if __name__ == '__main__':

    source_path = 'tool'
    style_name = 'test_midi_folder'

    test = InstScheduler(FoxDot.lib.Clock, source_path)
    test.AddMidiFolder(style_name)
    test.ChordOverride(['C', 'F', 'G', 'C'])

    # choose the playing mode
    # test.Ordered_event()
    # test.Random_event(2)
    test.Live_event()
    # test.set_tempo_pattern(4, 4)

    # testing routine for accuracy start
    c_time = time.time()
    loop_acc_test = threading.Timer(2, lambda: print(time.time() - c_time), ())
    loop_acc_test.daemon = True
    loop_acc_test.start()
    # testing routine for accuracy end

    test.StartInTime(2, 160)

    while(1):
        print('outside loop')
        time.sleep(2)
