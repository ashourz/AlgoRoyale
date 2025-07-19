import os
from logging.handlers import RotatingFileHandler


class CustomRotatingFileHandler(RotatingFileHandler):
    """
    Rotates log files as filename.log, filename2.log, filename3.log, etc.
    """

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        base, ext = os.path.splitext(self.baseFilename)

        # Find the next available log number
        i = 1
        while True:
            candidate = f"{base}{i}.log"
            if not os.path.exists(candidate):
                break
            i += 1

        # Rename the current log to the next available number
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, f"{base}{i}.log")

        # Reopen the stream
        self.mode = "a"
        self.stream = self._open()
