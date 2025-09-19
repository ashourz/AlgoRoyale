# Minimal mock logger implementing Loggable protocol


class MockLoggable:
    def __init__(self):
        self.messages = []

    def debug(self, msg, *args, **kwargs):
        m = f"DEBUG: {msg}"
        print(m)
        self.messages.append(m)

    def info(self, msg, *args, **kwargs):
        m = f"INFO: {msg}"
        print(m)
        self.messages.append(m)

    def warning(self, msg, *args, **kwargs):
        m = f"WARNING: {msg}"
        print(m)
        self.messages.append(m)

    def error(self, msg, *args, **kwargs):
        m = f"ERROR: {msg}"
        print(m)
        self.messages.append(m)

    def critical(self, msg, *args, **kwargs):
        m = f"CRITICAL: {msg}"
        print(m)
        self.messages.append(m)

    def exception(self, msg, *args, **kwargs):
        m = f"EXCEPTION: {msg}"
        print(m)
        self.messages.append(m)
