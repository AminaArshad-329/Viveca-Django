import os
import time


def append_zeros(val):
    count = len(str(val))
    diff = 6 - count
    name_val = str(val)
    if diff > 0:
        name_val = "0"
        for i in range(diff - 1):
            name_val = name_val + "0"
        name_val = name_val + str(val)
    return name_val


def create_storage_filename(prefix, filename):
    ext = os.path.splitext(filename)[-1]
    timestamp = int(time.time())  # Unix timestamp
    filename = f"{prefix}-{timestamp}{ext}"
    return filename
