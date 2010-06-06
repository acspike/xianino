class ETScale(object):
    def __init__(self, tones, root_frequency=55.0, octave_size=2.0):
        self.tones = tones
        self.octave_size = octave_size
        self.root_frequency = root_frequency
        self.title = "%s tone root of %s equal temperament at %s hz" % (self.tones, self.octave_size, self.root_frequency)
    def __call__(self, index):
        return self.root_frequency * (self.octave_size ** (index/float(self.tones)))

class ScalaScale(object):
    def __init__(self, scale_file, root_frequency=55.0, root_step = 0):
        self.tones = 1
        self.root_frequency = root_frequency
        self.root_step = root_step
        self.title = ''
        self.steps = [[1.0,1.0]]
        self.parse_errors = []
        self._parse(scale_file)
    def _parse(self, scala):
        #split scale discarding commments
        lines = [l.strip() for l in scala.strip().splitlines() if not l.strip().startswith('!')]

        #first line may be blank and contains the title
        self.title =  lines.pop(0)

        #second line indicates the number of note lines that should follow
        self.tones = int(lines.pop(0))

        #discard blank lines and anything following whitespace    
        lines = [l.split()[0] for l in lines if l != '']
        
        if len(lines) != self.tones:
            self.parse_errors.append('Error: expected %s more tones but found %s!' % (expected,len(lines)))
        else:
            for l in lines:
                #interpret anyline containing a dot as cents
                if l.find('.') >= 0:
                    num = 2**(float(l)/1200)
                    denom = 1
                #everything else is a ratio
                elif l.find('/') >=0:
                    l = l.split('/')
                    num = float(int(l[0]))
                    denom = float(int(l[1]))
                else:
                    num = float(int(l))
                    denom = 1.0
                self.steps.append([num,denom])
                
                if (num < 0) ^ (denom <= 0):
                    self.parse_errors.append('Error at "'+l+'": Negative and undefined ratios are not allowed!')
    def __call__(self, index):
        octave, step = divmod(index, self.tones)
        num, denom = self.steps[step]
        last_num, last_denom = self.steps[-1]
        return self.root_frequency * ((last_num/last_denom)**octave) * (num / denom)
