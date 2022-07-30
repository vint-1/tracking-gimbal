import datetime
import pathutils
import os
import csv

class TelemetryWriter():
    def open(self):
        raise NotImplementedError
    def write(self):
        raise NotImplementedError
    def close(self):
        raise NotImplementedError

class csvWriter(TelemetryWriter):
    def __init__(self, header = None, path = None):
        """
        contructor - creates a new csv file with appropriate timestamp if a path is not supplied
        """
        if path is None:
            filename = datetime.datetime.now().strftime("%y%m%d-%H-%M-telemetry.csv")
            path = os.path.join(pathutils.data_path, filename)
        self.path = path
        self.header = header

    def open(self, is_print = True):
        """
        opens csv file to write telemetry to
        """
        # create directories to store telemetry if they dont exist
        # if not os.path.exists(self.path):
            # os.makedirs(self.path, exist_ok = True)
        self.f = open(self.path, "at+")
        self.writer = csv.writer(self.f, delimiter = '\t')
        if self.f.tell() == 0 and self.header is not None: # file is empty, write a header
            self.writer.writerow(self.header)
        if is_print:
            print(f"writing telemetry to {self.path}")
    
    def write(self, data):
        """
        writes list of values to csv
        """
        self.writer.writerow(data)

    def close(self, is_print = True):
        self.f.close()
        if is_print:
            print(f"finished writing telemetry to {self.path}")
            

