import midibrain as mb
from scale import ETScale, ScalaScale
import sys

frontend = 'tk'
if 'tk' in sys.argv:
    frontend = 'tk'
elif 'pg' in sys.argv:
    frontend = 'pg'


if frontend == 'tk':
    from tkpiano import TKPiano as Piano
elif frontend == 'pg':
    from pgpiano import PGPiano as Piano
    import pygame
    pygame.init()


mb.init()

midi_brain = mb.MidiBrain()

#outdev=None
outdev=0

try:
    if outdev is None:
        print 'Output Devices:'
        for port in midi_brain.get_available_midi_output_ports():
            print port.index, port.name
        outdev = int(raw_input("Choose an output device: "))
    midi_brain.open_midi_output_port(outdev)
except:
    print "\nfailed to select midi output\n"
    raise

piano = Piano(midi_brain)
scale = '''test
25
100.
200.
300.
400.
500.
600.
700.
800.
900.
1000.
1100.
1200.
0.
112.
204.
316.
386.
498.
590. #610.
702.
814.
884.
996.
1088.
1200.'''
piano.scale = ScalaScale(scale, 55.0)

piano.keys = 'zsxdcvgbhnjm,w3e4rt6y7u8io'
piano.loop()

midi_brain.close_midi_output_port()

mb.quit()

if frontend == 'pg':
    pygame.quit()