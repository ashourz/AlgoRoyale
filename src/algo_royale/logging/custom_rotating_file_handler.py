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

        # Remove the oldest log if it exists
        oldest = f"{base}{self.backupCount}.log"
        if os.path.exists(oldest):
            os.remove(oldest)

        # Shift all logs up by one
        for i in range(self.backupCount - 1, 0, -1):
            src = f"{base}{'' if i == 1 else i}.log"
            dst = f"{base}{i + 1}.log"
            if os.path.exists(src):
                os.rename(src, dst)

        # Rename the current log to filename2.log
        if os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, f"{base}2.log")

        # Reopen the stream
        self.mode = "a"
        self.stream = self._open()
