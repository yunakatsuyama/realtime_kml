
import threading
from mock_datawrite import mock_losgatos
from write_KML import write_KML


device = "losgatos"
cfg = f"{device}" + ".cfg"


def datasave():
    if device == "losgatos":
        mock_losgatos("merge.txt", "Buffer")

def plot():
    write_KML(config_filename=cfg)  

if __name__ == "__main__":
    t1 = threading.Thread(target=datasave, daemon=False)
    t2 = threading.Thread(target=plot, daemon=True)

    t1.start()
    t2.start()

