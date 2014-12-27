import logging

class CountDecorator():
    def __init__(self, f):
        self.f = f
        self.count = 0

    def __call__(self, *args):
        logging.info('Call')
        self.count += 1
        return self.f(*args)

    def getCount(self):
        return self.count

    def reset(self):
        self.count = 0
