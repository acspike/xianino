import pygame

from piano import Piano

yellow = (255,255,0)
black = (0,0,0)
red = (255,0,0)
blue = (0,0,255)

class PGPiano(Piano):
    def __init__(self, midi_brain):
        Piano.__init__(self, midi_brain)
        
        size = (200,200)
        self.screen = pygame.display.set_mode(size)
        self.screen.fill(black)
        
    def loop(self):
        running = True
        while running:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                name = pygame.key.name(event.key)
                self.screen.fill(blue)
                self._piano_key_down(name)
            elif event.type == pygame.KEYUP:
                name = pygame.key.name(event.key)
                self.screen.fill(black)
                self._piano_key_up(name)
            pygame.display.flip()
