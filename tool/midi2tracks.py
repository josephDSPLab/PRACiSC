'''
Using midi2p to generate a Foxdot set with correspond midi

Require enviroment:
    Virtual midi port with sufficient number of port,
    Proper configuration for FoxDot in supercollider,
    and the proper mapping to the sound source in other software, e.g., Ableton.
'''
import os
from midi2p import midi2P
import FoxDot.lib


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
            tracks_Patterns = midi2P(file_path, None, verb=0)
            snd_abstract = FoxDot.lib.MidiOut(**tracks_Patterns[0], MidiNum=num_port_required)
            num_port_required += 1
            self.tracks_set.append(snd_abstract)

    def wrapping(self, config_path):
        if self.tracks_name:
            with open(config_path) as f:
                for line in f:
                    name, port = line.split(' ')[0], line.split(' ')[1]
                    if name in self.tracks_name or name[:-4] in self.tracks_name:
                        idx = self.tracks_name.index(name)
                        self.tracks_set[idx].kwargs['MidiNum'] = port
        return


if __name__ == '__main__':
    test = TrackSet('test_midi_folder')
    print(test.tracks_name)
