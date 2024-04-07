import pygame


class Timer:
    def __init__(self, id):
        self.id = id
        self.last_start_time = None
        self.duration_millis = None

    def pause(self):
        self.duration_millis = self.duration_millis - (
            pygame.time.get_ticks() - self.last_start_time
        )
        pygame.time.set_timer(self.id, 0)

    def resume(self):
        self.last_start_time = pygame.time.get_ticks()
        pygame.time.set_timer(self.id, self.duration_millis)

    def start(self, duration_millis):
        self.last_start_time = pygame.time.get_ticks()
        self.duration_millis = duration_millis
        pygame.time.set_timer(self.id, duration_millis)

    def stop(self):
        self.last_start_time = None
        self.duration_millis = None
        pygame.time.set_timer(self.id, 0)
