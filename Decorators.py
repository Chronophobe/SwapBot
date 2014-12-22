import logging

class CountDecorator():
    def __init__(self, f):
        self.f = f
        self.count = 0

    def __call__(self, *args, **kwargs):
        logging.info('Call')
        self.count += 1
        return self.f(self, *args, **kwargs)

    def getCount(self):
        return self.count

    def reset(self):
        self.count = 0
