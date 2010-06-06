import pypm
import math, time

def init():
    pypm.Initialize()
def quit():
    pypm.Terminate()
    
class NoFreeChannel(Exception):
    pass

class MidiPortDescription(object):
    def __init__(self, index, interface, name, direction, in_use):
        self.index = index
        self.interface = interface
        self.name = name
        self.direction = direction
        self.in_use = in_use

class NoteOn(object):
    def __init__(self, channel, note, pitch_bend, frequency):
        self.channel = channel
        self.note = note
        self.pitch_bend = pitch_bend
        self.frequency = frequency
    def __str__(self):
        return '<NoteOn chan=%s, note=%s, pb=%s, freq=%s>' % (self.channel,self.note,self.pitch_bend,self.frequency)

class MidiBrain(object):
    def __init__(self):
        self.pitch_bend_range_semitones=1
        self.pitch_bend_range_cents=0
        self.tuning_frequency=440
        self.tuning_note=69
        
        self.midi_output_port = None
        
        self.velocity = 100
        
        self._free_channels = set([0,1,2,3,4,5,6,7,8,10,11,12,13,14,15])
        self._used_channels = set([])
    
    def _write(self, status, data1, data2):
        if not self.midi_output_port:
            return
        self.midi_output_port.Write([[[status, data1, data2],pypm.Time()]])
    
    def _get_channel(self):
        try:
            channel = self._free_channels.pop()
            self._used_channels.add(channel)
            return channel
        except KeyError:
            raise NoFreeChannel
            
    def _return_channel(self, channel):
        self._used_channels.remove(channel)
        self._free_channels.add(channel)
        
    def _get_all_channels(self):
        return list(self._free_channels | self._used_channels)
        
    def _frequency_to_note_and_pitch_bend(self, frequency):
        base_frequency = self.tuning_frequency / (2.0 ** (self.tuning_note / 12.0))
        precise_note = 12.0 * math.log(frequency / base_frequency, 2)
        note = round(precise_note)
        pb = round(819200.0 * (precise_note - note) / ((100.0 * self.pitch_bend_range_semitones) + self.pitch_bend_range_cents)) + 8192
        return int(note), int(pb)

    def _get_midi_ports(self):
        ports = []
        for index in range(pypm.CountDevices()):
            interface, name, input, output, in_use = pypm.GetDeviceInfo(index)
            if input:
                direction = 'input'
            else:
                direction = 'output'
            ports.append(MidiPortDescription(index, interface, name, direction, in_use))
        return ports
    
    def get_available_midi_output_ports(self):
        return [port for port in self._get_midi_ports() if port.direction=='output' and not port.in_use]
    
    def open_midi_output_port(self, device_index, latency=20):
        self.midi_output_port = pypm.Output(device_index, latency)
        for channel in self._get_all_channels():
            #set course pitch bend range in semitones
            self._write(0xB0+channel,6,self.pitch_bend_range_semitones)
            #set fine pitch bend range in cents
            self._write(0xB0+channel,38,self.pitch_bend_range_cents)
    
    def close_midi_output_port(self):
        del self.midi_output_port
        self.midi_output_port = None
    
    def note_on(self, frequency):
        note, pitch_bend = self._frequency_to_note_and_pitch_bend(frequency)
        channel = self._get_channel()
        
        fine_pitch_bend = pitch_bend & 127
        corse_pitch_bend = (pitch_bend >> 7) & 127
        
        #set channel pitch bend
        self._write(0xE0+channel,fine_pitch_bend,corse_pitch_bend)
        #play note
        self._write(0x90+channel,note,self.velocity)
        
        return NoteOn(channel, note, pitch_bend, frequency)
    
    def note_off(self, channel, note):
        self._write(0x90+channel,note,0)
        self._return_channel(channel)
    
    def all_notes_off(self):
        for channel in self._get_all_channels():
            self._write(0xB0+channel,123,0)
    
    def exercise_scale(self, scale, note_time = 0.1, octaves = 1):
        tones = scale.tones * octaves
        indexes = range(tones) + range(tones-2,-1, -1)
        for i in indexes:
            note_on = self.note_on(scale(i))
            time.sleep(note_time)
            self.note_off(note_on.channel, note_on.note)