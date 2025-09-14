# Minimal mock logger implementing Loggable protocol
class MockLoggable:
    def debug(self, msg, *args, **kwargs):
        print(f"DEBUG: {msg}")

    def info(self, msg, *args, **kwargs):
        print(f"INFO: {msg}")

    def warning(self, msg, *args, **kwargs):
        print(f"WARNING: {msg}")

    def error(self, msg, *args, **kwargs):
        print(f"ERROR: {msg}")

    def critical(self, msg, *args, **kwargs):
        print(f"CRITICAL: {msg}")

    def exception(self, msg, *args, **kwargs):
        print(f"EXCEPTION: {msg}")
