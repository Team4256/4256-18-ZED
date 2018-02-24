from threading import Thread
class CustomThread(threading.Thread):
    def __init__(self, classWeWantToRun):
        Thread.__init__()
        self.classWeWantToRun = classWeWantToRun

    def run(self):
        self.classWeWantToRun.run()
