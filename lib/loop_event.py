'''Eventpipeline
To pipeline all the To-DO event and can return the next event
init
registers int

'''
import collections

class EventPipeline:
    def __init__(self):
        self.event_list = []
        self.eventcount = 0
        self.processed_count = 0
        self.running_event = None
        self.next_event = None
        self._proc = None
        self.running_done = True
    def PullEvent(self, method_name, args):
        if not  isinstance(method_name, collections.Iterable):
            method_name=[method_name]
        if not  isinstance(args, collections.Iterable):
            method_name=[args]
        self.event_list.append([method_name, args])
        self.eventcount += 1
        if self.next_event is None:
            self.next_event = [method_name, args]

    def Processor(self, func):
        '''
        func should be a callable object with knowing method_nam and corresponding args
        '''
        self._proc = func 
        return

    def sent_request(self,verb=0):
        '''
        To process the events in running_event 
        '''
        if verb > 0:
            print(self.next_event)
        #for method, args in zip(*self.next_event):
        #    print(method)
        #    print(args)
        self._proc(self.next_event[0], self.next_event[1])
        self.processed_count += 1
        if self.processed_count < len(self.event_list):
            self.next_event = self.event_list[self.processed_count]
        else:
            self.processed_count = 0
            self.next_event = self.event_list[0]