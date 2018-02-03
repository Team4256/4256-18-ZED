from networktables import NetworkTables
from queue import Empty

from CustomThread import Threadable
class ThreadableOdometrySender(Threadable):
    def __init__(self, table, odometry_queue):
        self.table = table
        self.table_position = self.table.getSubTable('Position')
        self.odometry_queue = odometry_queue
        self.enabled = False

    def run(self):
        self.enabled = True

        while self.enabled:
            new_position = self.odometry_queue.get(True)
            while True:
                try: new_position = self.odometry_queue.get_nowait()
                except Empty: break

            if new_position is not None:
                self.table_position.putNumber('Z', round(new_position[0], 4))
                self.table_position.putNumber('Y', round(new_position[1], 4))
                self.table_position.putNumber('X', -round(new_position[2], 4))
                # self.table_position.putNumber('Confidence', new_position[3])
                # self.table_position.putNumber('Timestamp', new_position[4])
                # self.table_position.putString('Tracking Status', new_position[5])
                self.odometry_queue.task_done()# TODO cannot just call here, have to it on every get

        self._release()

    def _release(self):
        self.table_position.clearPersistent('X')
        self.table_position.clearPersistent('Y')
        self.table_position.clearPersistent('Z')
        # self.table_position.clearPersistent('Confidence')
        # self.table_position.clearPersistent('Timestamp')
        # self.table_position.clearPersistent('Tracking Status')
        # self.table.deleteAllEntries()

    def stop(self):
        self.enabled = False

class ThreadableCubeSender(Threadable):
    def __init__(self, table, cube_queue):
        self.table = table.getSubTable('Cubes')
        self.cube_queue = cube_queue
        self.enabled = False

    def run(self):
        self.enabled = True

        while self.enabled:
            cubes = self.cube_queue.get(True)
            while True:
                try: cubes = self.cube_queue.get_nowait()
                except Empty: break

            if cubes is not None:
                self.table.putNumber('Left', cubes[0])
                self.table.putNumber('Right', cubes[1])
                self.cube_queue.task_done()

        self._release()

    def _release(self):
        self.table.clearPersistent('Left')
        self.table.clearPersistent('Right')

    def stop(self):
        self.enabled = False
