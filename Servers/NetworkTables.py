#{RobotPy}
from networktables import NetworkTables
#{OpenCV}
import cv2

class NetworkTables(object):
    def __init__(self, table, odometry_queue):
        self.table = table
        self.table_position = self.table.getSubTable('Position')
        self.odometry_queue = odometry_queue

    def run(self):
        while True:
            new_position = self.odometry_queue.get(True)
            if new_position is not None:
                self.table_position.putNumber('X', -round(new_position[0], 3))
                self.table_position.putNumber('Y', -round(new_position[1], 3))
                self.table_position.putNumber('Z', round(new_position[2], 3))
                self.table_position.putNumber('Confidence', new_position[3])

                self.table_position.putNumber('Timestamp', new_position[4])
                self.table_position.putString('Tracking Status', new_position[5])

    def release():
        table_position.clearPersistent('X')
        table_position.clearPersistent('Y')
        table_position.clearPersistent('Z')
        table_position.clearPersistent('Confidence')
        table_position.clearPersistent('Timestamp')
        table_position.clearPersistent('Tracking Status')
        table.deleteAllEntries()
