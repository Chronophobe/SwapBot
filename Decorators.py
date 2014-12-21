class CountDecorator():
    def __init__(self, f):
        self.f = f
        self.count = 0

    def __call__(self, *args):
        self.f(*args)
        self.count += 1

    def getCount(self):
        return self.count

    def reset(self):
        self.count = 0
