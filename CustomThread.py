from threading import Thread
class CustomThread(Thread):
    def __init__(self, classToRun):
        Thread.__init__(self)
        self.classToRun = classToRun

    def run(self):
        self.classToRun.run()

    def stop(self):
        self.classToRun.stop()
