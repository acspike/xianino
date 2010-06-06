from scale import ETScale, ScalaScale
from midibrain import NoFreeChannel

class Piano(object):
    def __init__(self, midi_brain):
        self.keys = '''zxcvbnm,./asdfghjkl;'qwertyuiop[]\`1234567890-='''
        self.playing = {}
        self.scale = ETScale(12, 25.5)
        
        self.midi_brain = midi_brain

    def loop(self):
        pass

    def _piano_key_down(self, name):
        index = self.keys.find(name)
        if len(name)!=1 or index<0:
            return
        if name in self.playing:
            return
        frequency = self.scale(index)
        try: 
            note_on = self.midi_brain.note_on(frequency)
        except NoFreeChannel:
            #print 'No Free Channel'
            return
        self.playing[name] = note_on
        
    def _piano_key_up(self, name):
        index = self.keys.find(name)
        if len(name)!=1 or index<0:
            return
        try:
            note_on = self.playing.pop(name)
            self.midi_brain.note_off(note_on.channel, note_on.note)
        except KeyError:
            pass
            #print 'error popping %s from %s' % (name, str(self.playing.keys()))
