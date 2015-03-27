from threading import Event, Thread
from random import random
from time import sleep
from .. import socketio, faw
from datetime import datetime

from gevent import monkey
monkey.patch_all()

#random number Generator Thread
thread = Thread()
thread_stop_event = Event()


class RandomThread(Thread):
    def __init__(self):
        self.delay = 400 #seconds change to 6000
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


class DataUpdateThread(Thread):
    def __init__(self):
        self.delay = 100 #seconds
        super(DataUpdateThread, self).__init__()

    def dataUpdate(self):
        """
        update the data every 10 minutes and emit to a threads instance (broadcast)
        Ideally to be run in a separate thread?
        """
        #infinite loop of data updates
        while not thread_stop_event.isSet():
            print('Data written to the server at ' + datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
            faw.write_matches_data()
            sleep(30)
            faw.write_standings_data()
            time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            socketio.emit('data_updated', {'data': time}, namespace='/test')


    def run(self):
        self.dataUpdate()
