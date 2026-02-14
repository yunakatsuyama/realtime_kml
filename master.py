
import threading
from mock_datawrite import mock_stream_to_buffer
from write_KML import write_KML

def datasave():
    mock_stream_to_buffer("merge.txt", "Buffer")

def plot():
    write_KML()   # your while True loop

if __name__ == "__main__":
    t1 = threading.Thread(target=datasave, daemon=False)
    t2 = threading.Thread(target=plot, daemon=True)

    t1.start()
    t2.start()

