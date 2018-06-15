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

import collections


def midinote2degree(m_note):
    (m_note - 60) // 12 * 7
    scale = {0: 0, 1: 0.5, 2: 1, 3: 1.5, 4: 2, 5: 3,
             6: 3.5, 7: 4, 8: 4.5, 9: 5, 10: 5.5, 11: 6}
    return (m_note - 60) // 12 * 7 + scale[int((m_note - 60) % 12)]


class single_note:

    def __init__(self, note, start_time, velocity=63, release_time=0, duration=0):
        self.note = note
        self.start_time = start_time
        self.release_time = release_time
        self.duration = duration
        self.velocity = velocity


class group_note:

    def __init__(self, group_note=None, velocity=None, start_time=0, release_time=None, duration=0):
        self.group_note = []
        self.start_time = start_time
        self.release_time = []
        self.duration = duration
        self.velocity = []

    def addnote(self, note):
        self.group_note.append(note.note)
        self.release_time.append(note.release_time)
        self.duration = np.maximum(self.duration, note.duration) if note.duration > 0 else note.duration
        self.velocity.append(note.velocity)

    def __str__(self):
        '''
        Format output
        '''
        float_format = '{:4.4f}, '
        int_format = '{:2d}, '
        output_str = ''
        output_str += 'Playing Notes:\n'
        output_str += '\t' + (len(self.group_note) *
                              int_format).format(*self.group_note) + '\n'
        output_str += 'Starting Beat:\n'
        output_str += '\t' + str(self.start_time) + '\n'
        output_str += 'Duration:\n'
        output_str += '\t' + str(self.duration) + '\n'
        output_str += 'Releasing Time:\n'
        output_str += '\t' + (len(self.release_time) *
                              float_format).format(*self.release_time) + '\n'
        output_str += 'Attacking Velocity:\n'
        output_str += '\t' + (len(self.velocity) *
                              int_format).format(*self.velocity) + '\n'
        return output_str

    def group2p(self):
        '''
        return a dictionary which is compatible to FoxDot
        '''
        import FoxDot
        P = {'degree': tuple([midinote2degree(n) for n in self.group_note]), 'dur': self.duration if self.duration > 0 else FoxDot.lib.rest(-self.duration),
             'sus': tuple(self.release_time), 'amp': tuple([(v+1.)/128 for v in self.velocity]),  'start_time': self.start_time}
        return P


class loop_note_seq:
    '''
    A class to deal with serializing the groups under some rules.
    method: 
        dur_valid: Checking for the on-off of each note is correct
        serialize: Forming a ordered-iterable container to the all notes
    '''

    def __init__(self, groups):
        self.groups = groups
        self.serial_groups = []
        if self.groups:
            self.serializing()

    def serializing(self):
        pre_start = -1

        for g in self.groups:
            if pre_start < 0:
                pre_start = g.start_time
                self.serial_groups.append(g)
            else:
                if self.serial_groups[-1].duration > 0:
                    self.serial_groups[-1].duration = g.start_time - pre_start
                pre_start = g.start_time
                self.serial_groups.append(g)
        self.serial_groups[-1].duration = 16 - pre_start

    def serial2P(self):
        '''
        return a iterable list which contains pattern-like parameters
        '''
        P_serial = {'degree': [], 'dur': [], 'sus': [], 'amp': [], 'start_time':[]}
        for s_g in [g.group2p() for g in self.serial_groups]:
            for key, value in P_serial.items():
                P_serial[key].append(s_g[key])
        return P_serial


def sortbytime(notes):
    notes = sorted(notes, key=lambda x: x.start_time)
    return notes


def grouping(notes, tol):
    current_start_time = 0

    current_group = group_note(start_time=current_start_time)
    group_collection = []
    if not notes:
        return 
    # Adding leading rest!
    if notes[0].start_time - 0 > tol:
        current_group.addnote(single_note(1, 1, duration=-notes[0].start_time,release_time=notes[0].start_time))

    
    for n in notes:
        if np.abs(n.start_time - current_start_time) > tol:
            current_start_time = n.start_time
            group_collection.append(current_group)
            current_group = group_note(start_time=current_start_time)
        current_group.addnote(n)
    if current_group.group_note:
        group_collection.append(current_group)
    return group_collection


def midi2P(path, track_num=None, verb=0):
    # midi file I/O
    mid = mido.MidiFile(path)
    #verb = 0
    current_note = {}
    note_collection = []
    if track_num is None:
        if len(mid.tracks) == 1:
            track_num = np.arange(1)
        else:
            track_num = np.arange(len(mid.tracks) - 1) + 1
    if track_num == 'all':
        track_num = np.arange(len(mid.tracks))

    tracks_Patterns = []

    # Only process the first track (the track of information is not counted)
    for i, track in enumerate([mid.tracks[t] for t in track_num]):
        if verb > 0:
            print('Track {}: {}'.format(i, track.name))
        time = 0.
        Is_first = True
        for msg in track:
            if msg.type == 'note_on':
                #print(msg)
                # accumulate the delta time first
                note_key = str(msg.note)
                if Is_first == False:
                    time += float(msg.time) / mid.ticks_per_beat
                else:
                    Is_first = False
                    if ((msg.time / mid.ticks_per_beat) % 16) > 0.16:
                        time += (msg.time / mid.ticks_per_beat) % 16

                if msg.velocity == 0:
                    if current_note[note_key][0]:
                        current_note[note_key][1].release_time = time - \
                            current_note[note_key][1].start_time
                        current_note[note_key][1].duration = np.ceil(
                            current_note[note_key][1].release_time)
                        current_note[note_key][0] = False
                        note_collection.append(current_note[note_key][1])
                # Currently, only consider the note a trigger
                else:
                    if note_key in current_note:
                        n_gap = time - current_note[note_key][1].start_time
                        if n_gap < current_note[note_key][1].duration:
                            current_note[note_key][1].duration = n_gap
                        if current_note[note_key][0]:
                            current_note[note_key][1].duration = n_gap
                            current_note[note_key][1].release_time = n_gap
                            current_note[note_key][0] = False
                            note_collection.append(current_note[note_key][1])
                    current_note[note_key]=[
                        True, single_note(msg.note, time, msg.velocity)]
                # checking all turned-on note, now we should force all of them to be turn off
        for key,n in current_note.items():
            if n[0]:
                n[1].duration = 16 - \
                    n[1].start_time
                n[1].release_time = 16 - \
                    n[1].start_time
                n[0] = False
                note_collection.append(n[1])
        note_collection = sortbytime(note_collection)
        if verb > 1:
            for i, note in enumerate(note_collection):
                print("# %2d: note is %d, start_time is %2.2f, release_time is %2.2f, duration is %2.2f" % (
                    i, note.note, note.start_time, note.release_time, note.duration))
        groups = grouping(note_collection, 1 / 8)
        if verb > 0:
            if not groups:
                break
            for i, g in enumerate(groups):
                print('--------------------------------------')
                print('# %2d Group:\n' % i)
                print(g)
                print(g.group2p())
            print('--------------------------------------')
            print('Form %2d note groups in this tack.' % len(groups))
        ser_group = loop_note_seq(groups)
        Patterns = ser_group.serial2P()
        if verb > 0:
            print(Patterns)
        tracks_Patterns.append(Patterns)
    return tracks_Patterns


if __name__ == '__main__':
    tracks_Patterns = midi2P('test_midi_folder\\Bass_1.mid','all', verb=2)
