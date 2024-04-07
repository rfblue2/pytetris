import pygame


class Timer:
    def __init__(self, id):
        self.id = id
        self.last_start_time = None
        self.duration_millis = None
        self.initial_duration_millis = None
        self.loops = None

    def pause(self):
        if self.duration_millis is not None:
            self.duration_millis = self.duration_millis - (
                pygame.time.get_ticks() - self.last_start_time
            )
            pygame.time.set_timer(self.id, 0)

    def resume(self):
        if self.duration_millis is not None:
            self.last_start_time = pygame.time.get_ticks()
            pygame.time.set_timer(self.id, self.duration_millis)

    def start(self, duration_millis, loops=0):
        self.last_start_time = pygame.time.get_ticks()
        self.duration_millis = duration_millis
        self.initial_duration_millis = duration_millis
        self.loops = loops
        pygame.time.set_timer(self.id, duration_millis, loops)

    def stop(self):
        self.last_start_time = None
        self.duration_millis = None
        self.loops = None
        pygame.time.set_timer(self.id, 0)

    def notify(self):
        """
        Notify should be called whenever the timer event is emitted in order
        to ensure the last start time is properly updated and that the
        repeating duration is set if the timer was paused midway in an interval.
        In general, this must be called on the event if the loops > 1
        (or loops = 0 for repeating timers)
        """
        if (
            self.duration_millis is not None
            and self.duration_millis is not self.initial_duration_millis
        ):
            if self.loops != 0:
                self.loops -= 1
            self.start(self.initial_duration_millis, self.loops)
