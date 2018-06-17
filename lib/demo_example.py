from InstSchduler import InstScheduler
import FoxDot
import time
import threading

source_path = 'tool'
style_name = 'test_midi_folder'

test = InstScheduler(FoxDot.lib.Clock, source_path)
test.AddMidiFolder(style_name)

''' chord modification, if you need it
# test.ChordOverride(['C', 'G', 'D', 'A', 'E'])
# test.ChordOverride(3)
'''

''' different scheduling mode
# choose the playing mode
# test.Ordered_event()      # Play the instruments by the reading order
# test.Random_event(2)      # Play the instrumnets by the random order
'''

test.Live_event()           # Online random playing event determined by prosperity function
test.set_tempo_pattern(4, 4) # if the meta file is exist, calling this routine is not required

# !!!!!!!! The upper part are recommended run at the early stage before some real-time processing
# For example, using Pyaudio to detect some pattern in real-time

''' testing routine for accuracy start (Not essential)
c_time = time.time()
loop_acc_test = threading.Timer(2, lambda: print(time.time() - c_time), ())
loop_acc_test.daemon = True
loop_acc_test.start()
testing routine for accuracy end
'''

test.StartInTime(2, 160) # First argument is when to play in sec.(from now)
                         # Second is the playing speed in BPM

# The routine is non-blocking. That is, you can do something else after
while(1):
    print('outside loop')
    time.sleep(2)