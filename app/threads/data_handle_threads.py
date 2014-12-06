from threading import Event, Thread
from random import random
from time import sleep
from .. import socketio

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()

class RandomThread(Thread):
    def __init__(self):
        self.delay = 600 #seconds
        super(RandomThread, self).__init__()

    def randomNumberGenerator(self):
        """
        Generate a random number every 100 second and emit to a threads instance (broadcast)
        Ideally to be run in a separate thread?
        """
        #infinite loop of magical random numbers
        print "Making random numbers"
        while not thread_stop_event.isSet():
            number = round(random()*10, 3)
            print number
            socketio.emit('newnumber', {'number': number}, namespace='/test')
            sleep(self.delay)

    def run(self):
        self.randomNumberGenerator()
