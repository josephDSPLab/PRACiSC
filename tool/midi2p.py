'''
Tool for convert Midi to readable pattern
midi -> sigle note represetation -> note group representation

single note representation:
------
attribute:
    note,
    velocity
    start_time: when to play the note (in beats),
    release_time: when to play the note (in beats),
    duration: the duration between current onset and next onset (in beats)
------

group note representation:
------
attribute:
    group_note = (note1, note2 ,... ,noteN),
    velocity = (v1, v2 ,...,vN),
    start_time: the common start_time for the note group,
    release_time: (r1, r2, ..., rN),
    duration: the common duration for the note group. 
              this value should be determined by the neighboring group
------
'''

import mido
import numpy as np


class single_note:

    def __init__(self, note, start_time, velocity, release_time=0, duration=0):
        self.note = note
        self.start_time = start_time
        self.release_time = release_time
        self.duration = duration
        self.velocity = velocity

class group_note:

    def __init__(self,group_note=None, velocity=None, start_time=0, release_time=None, duration=0):
        self.group_note = []
        self.start_time = start_time
        self.release_time = []
        self.duration = duration
        self.velocity = []
    def addnote(self,note):
        self.group_note.append(note.note)
        self.release_time.append(note.release_time)
        self.duration = np.maximum(self.duration, note.duration)
        self.velocity.append(note.velocity)
    def __str__(self):
        '''
        Format output
        '''
        float_format = '{:2.2f}, '
        int_format = '{:2d}, '
        output_str = ''
        output_str+='Playing Notes:\n'
        output_str+='\t'+(len(self.group_note) * int_format).format(*self.group_note)+'\n'
        output_str+='Starting Beat:\n'
        output_str+='\t'+str(self.start_time)+'\n'
        output_str+='Duration:\n'
        output_str+='\t'+str(self.duration)+'\n'
        output_str+='Releasing Time:\n'
        output_str+='\t'+(len(self.release_time) * float_format).format(*self.release_time)+'\n'
        output_str+='Attacking Velocity:\n'
        output_str+='\t'+(len(self.velocity) * int_format).format(*self.velocity)+'\n'
        return output_str
    def group2p(self):
        '''
        return a dictionary which is compatible to FoxDot
        '''
        P = {'midinote': tuple(self.group_note),'duration': self.duration,'sus': self.release_time,'vel':self.velocity}
        return P


def sortbytime(notes):
    notes = sorted(notes, key =lambda x : x.start_time)
    return notes

def grouping(notes,tol):
    current_start_time = 0
    current_group = group_note(start_time = current_start_time)
    group_collection = []
    for n in notes:
        if np.abs(n.start_time - current_start_time) > tol:
            current_start_time = n.start_time
            group_collection.append(current_group)
            current_group = group_note(start_time = current_start_time)
        current_group.addnote(n)
    group_collection.append(current_group)
    return group_collection


def midi2P(path):
    # midi file I/O
    mid = mido.MidiFile(path)
    verb = 1
    current_note = {}
    note_collection = []

    # Only process the first track (the track of information is not counted)
    for i, track in enumerate(mid.tracks[:2]):
        print('Track {}: {}'.format(i, track.name))
        time = 0.
        Is_first = True
        for msg in track:
            if msg.type == 'note_on':
                # accumulate the delta time first
                if Is_first == False:
                    time += float(msg.time) / mid.ticks_per_beat
                else:
                    Is_first = False

                if msg.velocity == 0:
                    if current_note[msg.note][0]:
                        current_note[msg.note][1].release_time = time - \
                            current_note[msg.note][1].start_time
                        current_note[msg.note][1].duration = np.ceil(current_note[msg.note][1].release_time)                            
                        current_note[msg.note][0] = False
                        note_collection.append(current_note[msg.note][1])
                # Currently, only consider the note a trigger
                else:
                    if msg.note in current_note:
                        n_gap = time - current_note[msg.note][1].start_time
                        if n_gap < current_note[msg.note][1].duration:
                            current_note[msg.note][1].duration = n_gap
                    current_note[msg.note] = [
                        True, single_note(msg.note, time, msg.velocity)]
        note_collection = sortbytime(note_collection)
        if verb > 1:
            for i, note in enumerate(note_collection):
                print("# %2d: note is %d, start_time is %2.2f, release_time is %2.2f, duration is %2.2f"  % (
                    i, note.note,note.start_time,note.release_time,note.duration))
        groups = grouping(note_collection, 1/8)
        for i, g in enumerate(groups):
            print('--------------------------------------')
            print('# %2d Group:\n' % i)
            print(g)
            print(g.group2p())
        print('--------------------------------------')

if __name__ == '__main__':
    midi2P('chord_4.mid')
