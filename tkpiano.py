import Tkinter

from scale import ETScale, ScalaScale
from midibrain import NoFreeChannel

class TKPiano(object):
    def __init__(self, midi_brain):
        self.keys = '''zxcvbnm,./asdfghjkl;'qwertyuiop[]\`1234567890-='''
        self.playing = {}
        self.scale = ETScale(12, 25.5)
        
        self.midi_brain = midi_brain
        
        self.root = Tkinter.Tk()
        self.root.title('xianino')

        self.root.bind('<Key>', self._on_key_down)
        self.root.bind('<KeyRelease>', self._on_key_up)

        # This is a bit of a hack to detect key events that occur when 
        # when a key is held depressed
        # 
        # When a key is pressed and released repeatedly the serial number in the event
        # differs for each event, down and up and the next down, etc
        # When a key is held the each following down and its immediately preceeding up
        # share a serial number
        #
        # To detect this we delay the processing of up events slightly hoping that 
        # the corresponding down event for a held key will fire in the meantime
        #
        # This is all terribly confusing. :-)
        #
        # http://wiki.tcl.tk/20299
        self.key_up_delay = 5
        self.key_down_serials = {}
    
    def loop(self):
        self.root.mainloop()

    def _on_key_down(self, ke):
        name = ke.char

        # store this serial number for comparison with the previous up event
        self.key_down_serials[name] = ke.serial

	if name in self.playing:
            return

        if ke.keysym == 'BackSpace':
            self.midi_brain.exercise_scale(self.scale)
            return
        index = self.keys.find(name)
        if len(name)!=1 or index<0:
            return
        frequency = self.scale(index)
        try: 
            note_on = self.midi_brain.note_on(frequency)
        except NoFreeChannel:
            #print 'No Free Channel'
            return
        self.playing[name] = note_on

    def _on_key_up(self, ke):
        # call _after_key_up with a slight delay in the hope that we will
        # recieve the associated keypress event for a held key before it fires
        self.root.after(self.key_up_delay, self._after_key_up, ke)
    def _after_key_up(self, ke):
        name = ke.char

        # if we received a matching down serial while we waited
        if ke.serial==self.key_down_serials[name]:
            return

        index = self.keys.find(name)
        if len(name)!=1 or index<0:
            return
        try:
            note_on = self.playing.pop(name)
            self.midi_brain.note_off(note_on.channel, note_on.note)
        except KeyError:
            pass
            #print 'error popping %s from %s' % (name, str(self.playing.keys()))
