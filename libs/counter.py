class counter:
    def __init__(self, x: int = 0, y: int = 3):
        self.x = x
        self.y = y
    
    def current(self):
        c, v = self.x, self.y
        next_y = (self.y + 3) % 16
        if self.y + 3 >= 16:
            self.x = (self.x + 1) % 16
        self.y = next_y
        return c, v
 