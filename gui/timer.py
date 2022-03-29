from pygame.time import get_ticks, wait

class Timer:
    def __init__(self, period: float):
        self.period = period * 1000
        self.time_last = 0
    
    def wait(self):
        time_now = get_ticks()
        dt = time_now - self.time_last
        if (dt < self.period):
            wait(int(self.period - dt))
            self.time_last = time_now + self.period
        else:
            self.time_last = time_now
        
