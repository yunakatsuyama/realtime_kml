
import os
import time
import shutil
from datetime import datetime

def mock_stream_to_buffer(input_file, buffer_folder="Buffer"):
    os.makedirs(buffer_folder, exist_ok=True)

    with open(input_file, "r") as f:
        header = f.readline().strip()

        for line in f:
            line = line.strip()
            if not line:
                continue

            time_utc_str = line.split(",")[0]
            dt = datetime.strptime(time_utc_str, "%Y-%m-%d %H:%M:%S")
            filename = dt.strftime("%Y%m%d_%H%M%S") + ".csv"

            tmp_path = os.path.join(buffer_folder, filename + ".tmp")
            final_path = os.path.join(buffer_folder, filename)

            with open(tmp_path, "w") as out:
                out.write(header + "\n")
                out.write(line + "\n")

            os.replace(tmp_path, final_path)  # atomic write

            print("Saved raw:", final_path)
            time.sleep(1)
# run.
if __name__ == "__main__":
    
    mock_stream_to_buffer("merge.txt")            