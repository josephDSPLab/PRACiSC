'''
Scheduler
Used for the controling the music event on time

'''

import threading
import sched
import time
import FoxDot
import os
from loop_event import EventPipeline
from tool.midi2p import midi2P
from tool.midi2tracks import TrackSet


class InstScheduler():

    def __init__(self, FoxDot_clock=FoxDot.lib.Clock):
        self.s = sched.scheduler(time.time, time.sleep)
        self.fclock = FoxDot_clock
        self.Inst_dict = {}
        self.player_dict = {}
        self.parameters = {}
        self.playing_flag = {}
        self.pipeline = EventPipeline()
        self.pipeline.Processor(self.EventProcessor)


    def __getitem__(self, Inst_name):
        return self.Inst_dict[Inst_name]
    def __str__(self):
        out_str = 'Current Registerd Inst:\n\n'
        out_str+=str(self.Inst_dict.keys())
        return out_str

    def AddInst(self, Inst_name, Instcontrol,**kwargs):
        '''
        Note: Automatically overwrite
        '''
        self.Inst_dict[Inst_name] = Instcontrol
        p = {}
        for key, value in kwargs.items():
            p[key] = value
        self.parameters[Inst_name] = p
        if Inst_name not in self.player_dict:
            self.player_dict[Inst_name] = FoxDot.lib.Player()
        self.playing_flag[Inst_name] = False

    def PlayInst(self,Inst_name):
        self.player_dict[Inst_name] >> self.Inst_dict[Inst_name](**self.parameters[Inst_name])
        self.playing_flag[Inst_name] = True

    def AddMidi(self,Inst_name,port_num):
        Patterns = midi2P(file_path, None, verb=0)
        Patterns[0]['MidiNum']=port_num
        self.AddInst(Inst_name, FoxDot.lib.MidiOut, **Patterns[0])

    def AddMidiFolder(self, folder_path):
        test = TrackSet(folder_path)
        wrap_path = os.path.join(folder_path,'SC_Abelton.txt')
        test.wrapping(wrap_path)
        for n,p in zip(test.tracks_name,test.tracks_set):
            self.AddInst(n, FoxDot.lib.MidiOut, **p[0])

    def change_parameters(self, Inst_name, **kwargs):
        for key, value in kwargs.items():
            self.parameters[Inst_name][key] = value
        if self.playing_flag[Inst_name]:
            self.PlayInst(Inst_name)

    def StopInst(self,Inst_name):
        self.player_dict[Inst_name].stop()
        self.playing_flag[Inst_name] = False

    def EventProcessor(self, event_type,event_arg):
        '''
        read Score from data -> do the correspond method
        '''

        '''
        Read-In and pipeline
        '''

        '''
        Action
        '''
        if hasattr(event_type,'__iter__') == False:
            event_type = [event_type]
        if hasattr(event_arg,'__iter__') == False:
            event_type = [event_arg]
        for e,arg in zip(event_type,event_arg):
            if e == 'Play':
                if arg['Inst_name'] not in self.Inst_dict:
                    self.AddInst(**arg)
                self.PlayInst(Inst_name = arg['Inst_name'])
            if e == 'Stop':
                self.StopInst(**arg)
            if e == 'ChangeParameter':
                self.change_parameters(**arg)

        return
    def Odered_event(self):

        for k in self.Inst_dict.keys():
            self.pipeline.PullEvent(['Play'], [{'Inst_name':k}])
        return

    def Random_event(self):
        '''
        Define a prosperity function which can limit the current number of playing Instruments
        '''
        num_point = 5
        min_pos = 0.2
        max_pos = 1
        Pros_tri = np.linspace(min_pos,max_pos, num=(num_point-1)/2)
        pros = np.concatenate([Pros_tri,Pros_tri.reverse()])

        for k in self.Inst_dict.keys():
            self.pipeline.PullEvent()

    def CheckingAsyLoop(self, beat_bar=4, bar_loop=4):
        '''
        Asynchronous main loop for checking the event online
        '''
        #self.play_bpm = self.fclock.bpm = play_bpm
        #self.fclock.set_time(0)
        self.pipeline.sent_request()
        self.fclock.set_time(-0.5)
        self.start_time = time.time()
        loop_dur = beat_bar * bar_loop * (60. / self.fclock.bpm)

        sleep_time = loop_dur / 2.
        '''x
        #self.Eventpipeline(['Play'],[{'Inst_name':'space1', 'Instcontrol': FoxDot.lib.space,
        #        'degree': [0,1,2,3]}])
        self.EventProcessor(['Play'],[{'Inst_name':'Bass_3.mid'}])
        time_wait = 2 - ((time.time() - self.start_time) % 2)
        time.sleep(time_wait)
        T = 1
        while(1):
            if T==1:
                T=0
                self.EventProcessor(['Play'],[{'Inst_name':'Chord_1.mid'}])
                self.EventProcessor(['Stop'],[{'Inst_name':'Bass_3.mid'}])
            else:
                T=1
                self.EventProcessor(['Play'],[{'Inst_name':'Bass_3.mid'}])
                self.EventProcessor(['Stop'],[{'Inst_name':'Chord_1.mid'}])
            #self.s.enter(0.5, 1, lambda: print('testing message'), ())
            #self.s.run()
            time_wait = 2 - ((time.time() - self.start_time) % 2)
            time.sleep(time_wait)
        '''
        while(1):
            time_wait = sleep_time - ((time.time() - self.start_time) % sleep_time)
            time.sleep(time_wait)
            time_take = loop_dur - ((time.time() - self.start_time) % loop_dur)
            self.s.enter(time_take,1,self.pipeline.sent_request, (0,))
            self.s.run()
            
        return

    def StartInTime(self, delay_time, play_bpm):
        '''
        Start the event pipeline after delay_time directly
        '''
        self.fclock.set_time(-0.1)
        self.play_bpm = self.fclock.bpm = play_bpm
        #self.start_time = time.time()
        loop_thread = threading.Timer(delay_time, self.CheckingAsyLoop, ())
        loop_thread.daemon=True
        loop_thread.start()
        return 



if __name__ == '__main__':
    
    test = InstScheduler(FoxDot.lib.Clock)
    test.AddMidiFolder('tool\\Midinote-Test2')
    print(test)
    test.Odered_event()
    test.StartInTime(2, 140)
    while(1):
        print('outside loop')
        time.sleep(2)
    

