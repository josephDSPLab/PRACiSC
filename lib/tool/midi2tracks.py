'''
Using midi2p to generate a Foxdot set with correspond midi

Require enviroment:
    Virtual midi port with sufficient number of port,
    Proper configuration for FoxDot in supercollider,
    and the proper mapping to the sound source in other software, e.g., Ableton.
'''
import os

import FoxDot.lib
if __name__ == '__main__':
    from midi2p import midi2P
else:
    from .midi2p import midi2P


class TrackSet:
    '''
    TrackSet construct a collection of patterns which are read from midi files.
    To wrap each track to correct midi port, please give a text file describe the connection:
        midi_file_name1 midi_port_number1
        midi_file_name2 midi_port_number2
        ... ...

    '''

    def __init__(self, folder_path):
        destination = os.listdir(folder_path)
        num_port_required = 0
        self.tracks_set = []
        self.tracks_name = []
        for data in destination:
            if not data.endswith('.mid'):
                continue
            self.tracks_name.append(data)
            file_path = os.path.join(folder_path, data)
            Patterns = midi2P(file_path, None, verb=0)

            Patterns[0]['MidiNum']=num_port_required
            num_port_required += 1
            self.tracks_set.append(Patterns)
    def P2FoxDot(self):
        '''
        Return a list contains FoxDot Midi object constructed by the track_set parameters
        '''
        return [FoxDot.lib.MidiOut(**p) for p in tracks_set]

    def wrapping(self, config_path):
        print("Midi Port wrapping:\n")
        if self.tracks_name:
            with open(config_path) as f:
                for line in f:
                    name, port = line.split(' ')[0], line.split(' ')[1]
                    if name in self.tracks_name or name[:-4] in self.tracks_name:
                        idx = self.tracks_name.index(name)
                        self.tracks_set[idx][0]['MidiNum'] = int(port) -1 
                        print(name,int(port))
        return


if __name__ == '__main__':
    test = TrackSet('test_midi_folder')
    print(test.tracks_name)
