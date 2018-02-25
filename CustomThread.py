from threading import Thread
class CustomThread(Thread):
    def __init__(self, classWeWantToRun):
        Thread.__init__(self)
        self.classWeWantToRun = classWeWantToRun

    def run(self):
        self.classWeWantToRun.run()
