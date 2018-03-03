from networktables import NetworkTables
from queue import Empty

class ThreadableOdometrySender(object):
    def __init__(self, table, odometry_queue):
        self.table = table
        self.table_position = self.table.getSubTable('Position')
        self.odometry_queue = odometry_queue
        self.enabled = False

    def run(self):
        self.enabled = True

        while self.enabled:
            if self.odometry_queue.empty():
                new_position = self.odometry_queue.get(True)
            else:
                while True:
                    try:
                        new_position = self.odometry_queue.get_nowait()
                    except Empty:
                        break

            if new_position is not None:
                self.table_position.putNumber('Y', round(new_position[0], 4))
                self.table_position.putNumber('X', -round(new_position[1], 4))
                self.table_position.putNumber('Z', round(new_position[2], 4))
                self.table_position.putNumber('Confidence', new_position[3])
                self.table_position.putNumber('Timestamp', new_position[4])
                self.table_position.putString('Tracking Status', new_position[5])

            self.odometry_queue.task_done()# TODO cannot just call here, have to it on every get

        self._release()

    def _release(self):
        self.table_position.clearPersistent('X')
        self.table_position.clearPersistent('Y')
        self.table_position.clearPersistent('Z')
        self.table_position.clearPersistent('Confidence')
        self.table_position.clearPersistent('Timestamp')
        self.table_position.clearPersistent('Tracking Status')
        # self.table.deleteAllEntries()

    def stop(self):
        self.enabled = False
