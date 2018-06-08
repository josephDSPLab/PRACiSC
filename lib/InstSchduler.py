'''
Scheduler
Used for the controling the music event on time

'''
import sched
import schedule
import threading
import time
import FoxDot


class InstScheduler():

    def __init__(self, FoxDot_clock=FoxDot.lib.Clock):
        self.s = sched.scheduler(time.time, time.sleep)
        self.fclock = FoxDot_clock
        self.Inst_dict = {}
        self.player_dict = {}
        self.parameters = {}
        self.playing_flag = {}


    def __getitem__(self, Inst_name):
        return self.Inst_dict[Inst_name]        

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

    def change_parameters(self, Inst_name, **kwargs):
        for key, value in kwargs.items():
            self.parameters[Inst_name][key] = value
        if self.playing_flag[Inst_name]:
            self.PlayInst(Inst_name)

    def StopInst(self,Inst_name):
        self.player_dict[Inst_name].stop()
        self.playing_flag[Inst_name] = False

    def AddEvent(self, Inst_name, delay_beat):
        
        return

    def Eventpipeline(self, event_type,event_arg):
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
        for e,arg in zip(event_type,event_arg):
            if e == 'Play':
                self.AddInst(**arg)
                self.PlayInst(Inst_name = arg['Inst_name'])
            if e == 'Stop':
                self.StopInst(**arg)
            if e == 'ChangeParameter':
                self.change_parameters(**arg)

        return

    def CheckingAsyLoop(self):
        '''
        Asynchronous main loop for checking the event online
        '''
        self.Eventpipeline(['Play'],[{'Inst_name':'space1', 'Instcontrol': FoxDot.lib.space,
                'degree': [0,1,2,3]}])
        T = 1
        while(1):
            if T==1:
                T=0
                self.Eventpipeline(['ChangeParameter'],[{'Inst_name':'space1',
                'degree': [4,5,6,7]}])
            else:
                T=1
                self.Eventpipeline(['Play'],[{'Inst_name':'space1', 'Instcontrol': FoxDot.lib.space,
                'degree': [0,1,2,3]}])
            #self.s.enter(0.5, 1, lambda: print('testing message'), ())
            #self.s.run()
            time_wait = 2 - ((time.time() - self.start_time) % 2)
            time.sleep(time_wait)
        return

    def StartInTime(self, delay_time, play_bpm):
        '''
        Start the event pipeline after delay_time directly
        '''
        self.play_bpm = self.fclock = play_bpm
        self.start_time = time.time()
        loop_thread = threading.Timer(delay_time, self.CheckingAsyLoop, ())
        loop_thread.daemon=True
        loop_thread.start()
        return 



if __name__ == '__main__':
    
    test = InstScheduler(FoxDot.lib.Clock)
    test.StartInTime(2, 120)
    while(1):
        print('outside loop')
        time.sleep(2)
    

