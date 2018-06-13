'''Eventpipeline
To pipeline all the To-DO event and can return the next event
init
registers int

'''
import collections
import numpy as np


class EventPipeline:

    def __init__(self):
        self.event_clear()

        # processor init
        self._proc = None
        self._timer = None

    def event_clear(self):
        self.event_list = []
        self.eventcount = 0
        self.processed_count = 0
        self.running_event = None
        self.next_event = None
        self.running_done = True

    def PushEvent(self, method_name, args, time_stamp, vol=False):
        '''
        time_stamp: integer type, when to do the process
        '''
        if not isinstance(method_name, collections.Iterable):
            method_name = [method_name]
        if not isinstance(args, collections.Iterable):
            method_name = [args]
        event = {'method': method_name, 'args': args,
                 'time_stamp': time_stamp, 'volatile': vol}
        self.event_list.append(event)
        self.eventcount += 1
        if self.next_event is None:
            self.next_event = self.event_list[-1]

    def InsertEvent(self, method_name, args, time_stamp, vol=False, loc='head'):
        if loc == 'head':
            idx = next((i for i, e in enumerate(self.event_list) if int(
                e['time_stamp']) >= int(time_stamp)), self.eventcount)
        if loc == 'tail':
            idx = next(i for i, e in enumerate(self.event_list)
                       if e['time_stamp'] >= time_stamp)
        event = {'method': method_name, 'args': args,
                 'time_stamp': time_stamp, 'volatile': vol}
        self.event_list.insert(idx, event)
        self.eventcount += 1
        if self.next_event is None:
            self.next_event = self.event_list[-1]
        if self.next_event['time_stamp'] >= time_stamp:
            self.next_event = self.event_list[idx]

    def Processor(self, func, timer):
        '''
        func should be a callable object with knowing method_nam and corresponding args
        '''
        self._proc = func
        self._timer = timer
        return

    def sent_request(self, event_idx = None, verb=0):
        '''
        To process the events in running_event 
        '''
        if verb > 0:
            print(self.next_event)
        # Check if the current time_stamp is valid
        if np.round(self._timer() - self.next_event['time_stamp']) >= 0:
            self._proc(self.next_event['method'], self.next_event['args'])
            self.processed_count += 1
        else:
            return 0
        # Check if it is the end of the event_list
        if self.processed_count < self.eventcount:
            self.next_event = self.event_list[self.processed_count]
        else:
            self.processed_count = 0
            self.next_event = self.event_list[0]

        # Check if it is needed to succeed to the next event
        if self.next_event['time_stamp'] == self.event_list[self.processed_count - 1]['time_stamp']:
            cont = 1
        else:
            cont = 0

        # Check if the event is volatile
        if self.event_list[self.processed_count - 1]['volatile']:
            del self.event_list[self.processed_count - 1]
            self.eventcount -= 1
            self.processed_count -= 1

        # return the continue flag value
        return cont
