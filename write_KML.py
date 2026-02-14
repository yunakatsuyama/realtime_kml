# Icon url https://kml4earth.appspot.com/icons.html

import pandas as pd
import numpy as np
import time
import os
import shutil
from datetime import datetime

def sync_buffer_to_local(buffer_dir="Buffer", local_dir="LocalBuffer"):
    os.makedirs(local_dir, exist_ok=True)

    for f in os.listdir(buffer_dir):
        src = os.path.join(buffer_dir, f)
        dst = os.path.join(local_dir, f)

        if not os.path.exists(dst):
            shutil.copy2(src, dst)

def local_data_reader(local_dir="LocalBuffer"):
    files = sorted(os.listdir(local_dir))

    for fname in files:
        path = os.path.join(local_dir, fname)
        with open(path, "r") as f:
            lines = f.readlines()
            if len(lines) > 1:
                yield lines[1].strip()   # skip header



colors = ["ff0000ff", "ff00ffff", "ff00ff00", "ff00ff00", "ff0000ff"]

def init_kml_5step(filename):
    tmp = filename + ".tmp"

    styles = """
<Style id="CH4_1C2H6_1"><IconStyle><color>ff0000ff</color><scale>0.2</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_1C2H6_2"><IconStyle><color>ff00ffff</color><scale>0.2</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_1C2H6_3"><IconStyle><color>ff00ff00</color><scale>0.2</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_1C2H6_4"><IconStyle><color>ff00ffff</color><scale>0.2</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_1C2H6_5"><IconStyle><color>ff0000ff</color><scale>0.2</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>

<Style id="CH4_2C2H6_1"><IconStyle><color>ff0000ff</color><scale>0.4</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_2C2H6_2"><IconStyle><color>ff00ffff</color><scale>0.4</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_2C2H6_3"><IconStyle><color>ff00ff00</color><scale>0.4</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_2C2H6_4"><IconStyle><color>ff00ffff</color><scale>0.4</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_2C2H6_5"><IconStyle><color>ff0000ff</color><scale>0.4</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>

<Style id="CH4_3C2H6_1"><IconStyle><color>ff0000ff</color><scale>0.6</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_3C2H6_2"><IconStyle><color>ff00ffff</color><scale>0.6</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_3C2H6_3"><IconStyle><color>ff00ff00</color><scale>0.6</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_3C2H6_4"><IconStyle><color>ff00ffff</color><scale>0.6</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_3C2H6_5"><IconStyle><color>ff0000ff</color><scale>0.6</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>

<Style id="CH4_4C2H6_1"><IconStyle><color>ff0000ff</color><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_4C2H6_2"><IconStyle><color>ff00ffff</color><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_4C2H6_3"><IconStyle><color>ff00ff00</color><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_4C2H6_4"><IconStyle><color>ff00ffff</color><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_4C2H6_5"><IconStyle><color>ff0000ff</color><scale>0.8</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>

<Style id="CH4_5C2H6_1"><IconStyle><color>ff0000ff</color><scale>1.0</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_5C2H6_2"><IconStyle><color>ff00ffff</color><scale>1.0</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_5C2H6_3"><IconStyle><color>ff00ff00</color><scale>1.0</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_5C2H6_4"><IconStyle><color>ff00ffff</color><scale>1.0</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
<Style id="CH4_5C2H6_5"><IconStyle><color>ff0000ff</color><scale>1.0</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href></Icon></IconStyle><LabelStyle><scale>0</scale></LabelStyle></Style>
"""

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>Realtime Track</name>
{styles}
<Folder>
<!-- INSERT_HERE -->
</Folder>
</Document>
</kml>
"""
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)

    os.replace(tmp, filename)


def ch4_to_step(ch4, vmin=1.9, vmax=2.1):
    steps = 5
    step = int((ch4 - vmin) / (vmax - vmin) * steps) + 1
    step = max(1, min(5, step))  
    return step

def c2h6_to_step(c2h6, vmin= -1.8, vmax = 1.8):
    steps = 5
    step = int((c2h6 - vmin) / (vmax - vmin) * steps) + 1
    step = max(1, min(5, step))  
    return step
def add_point_5step(lat, lon, name, ch4, c2h6, alt, data_dict, filename="merge2.kml"):
    """
    data_dict: {column_name: value, ...}
    """
    ch4_step = ch4_to_step(ch4)
    c2h6_step = c2h6_to_step(c2h6)
    style_id = f"CH4_{ch4_step}C2H6_{c2h6_step}"

    
    table_rows = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in data_dict.items()])
    html_table = f"<table border='1'>{table_rows}</table>"

    tmp = filename + ".tmp"

    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    placemark = f"""
<Placemark>
  <name>{name}</name>
  <styleUrl>#{style_id}</styleUrl>
  <description><![CDATA[{html_table}]]></description>
  <Point>
    <extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <coordinates>{lon},{lat},{alt}</coordinates>
  </Point>
</Placemark>
"""

    new_text = text.replace(
        "<!-- INSERT_HERE -->",
        placemark + "\n<!-- INSERT_HERE -->"
    )

    with open(tmp, "w", encoding="utf-8") as f:
        f.write(new_text)

    os.replace(tmp, filename)

def write_current_pointer(all_files, active_index):
    """
    all_files: list of KML filenames in order [merge3d_1.kml, merge3d_2.kml, ...]
    active_index: index of currently live file (0-based)
    """
    links = []

    # Old files (frozen)
    for i, f in enumerate(all_files[:active_index]):
        links.append(f"""
  <NetworkLink>
    <name>{f} (frozen)</name>
    <Link>
      <href>{f}</href>
      <refreshMode>onExpire</refreshMode>
    </Link>
  </NetworkLink>""")

    # Active file (live)
    active_file = all_files[active_index]
    links.append(f"""
  <NetworkLink>
    <name>{active_file} (live)</name>
    <Link>
      <href>{active_file}</href>
      <refreshMode>onInterval</refreshMode>
      <refreshInterval>1</refreshInterval>
    </Link>
  </NetworkLink>""")

    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
{''.join(links)}
</Document>
</kml>
"""

    with open("current.kml.tmp", "w", encoding="utf-8") as f:
        f.write(content)
    os.replace("current.kml.tmp", "current.kml")

# == Main ===========
def write_KML():
    points_per_file = 300
    file_index = 0
    point_counter = 0
    all_files = []

    # Initialize first file
    file_index += 1
    kmlfile = f"merge3d_{file_index}.kml"
    all_files.append(kmlfile)
    init_kml_5step(kmlfile)

    write_current_pointer(all_files, active_index=0)

    processed_files = set()

    while True:

        # Sync raw data
        sync_buffer_to_local()

        files = sorted(os.listdir("LocalBuffer")) # files are the current entire
        new_files = files[(file_index-1) * 300 :] # the lastest 300


        # Read new files
        for fname in new_files:

            if fname in processed_files:
                continue

            processed_files.add(fname)

            with open(os.path.join("LocalBuffer", fname), "r") as f:
                lines = f.readlines()
                if len(lines) < 2:
                    continue

                line = lines[1].strip()

            cols = line.split(",")

            lat = float(cols[2])
            lon = float(cols[3])
            alt = float(cols[4])
            ch4 = float(cols[9])
            c2h6 = float(cols[12])

            data_dict = {
                "Time_UTC": cols[0],
                "CH4_ppm": cols[9],
                "C2H6_ppb": cols[12]
            }

            add_point_5step(lat, lon, cols[0], ch4, c2h6, alt, data_dict, kmlfile)

            point_counter += 1

            #Rotate file every 300 points
            if point_counter >= points_per_file:

                point_counter = 0
                file_index += 1

                kmlfile = f"merge3d_{file_index}.kml"
                all_files.append(kmlfile)

                init_kml_5step(kmlfile)

                # update current.kml ONLY when switching file
                write_current_pointer(all_files, active_index=file_index-1)

        time.sleep(1)

## == Main =============
if __name__ == "__main__":
    write_KML()
    # # == Main ========
    # points_per_file = 300
    # file_index = 0
    # point_counter = 0
    # all_files = []

    # # Start first file
    # file_index += 1
    # kmlfile = f"merge3d_{file_index}.kml"
    # all_files.append(kmlfile)
    # init_kml_5step(kmlfile)

    # # First file is live
    # write_current_pointer(all_files, active_index=0)

    # for line in mock_dataread(filename):
    #     cols = line.split(",")

    #     lat = float(cols[2])
    #     lon = float(cols[3])
    #     alt = float(cols[4])
    #     ch4 = float(cols[9])
    #     c2h6 = float(cols[12])

    #     data_dict = {
    #         "Time_UTC": cols[0],
    #         "Time_EPOCH": cols[1],
    #         "Latitude": cols[2],
    #         "Longitude": cols[3],
    #         "Altitude": cols[4],
    #         "WindU": cols[5],
    #         "WindV": cols[6],
    #         "Temperature_C": cols[7],
    #         "RH_percent": cols[8],
    #         "CH4_ppm": cols[9],
    #         "CO2_ppm": cols[10],
    #         "H2O_percent": cols[11],
    #         "C2H6_ppb": cols[12],
    #         "Heading_deg": cols[13],
    #         "GrdSpeed_mps": cols[14],
    #         "AGL_m": cols[15],
    #         "BLIndex_m": cols[16]
    #     }

    #     add_point_5step(lat, lon, cols[0], ch4, c2h6, alt, data_dict, kmlfile)

    #     point_counter += 1

    #     if point_counter >= points_per_file:
    #         # Move to next file
    #         point_counter = 0
    #         file_index += 1
    #         kmlfile = f"merge3d_{file_index}.kml"
    #         all_files.append(kmlfile)
    #         init_kml_5step(kmlfile)

    #         # Update current.kml: all previous frozen, last one live
    #         write_current_pointer(all_files, active_index=file_index-1)




    # == Main  (old) ====
    # init_kml_5step(kmlfile)

    # for line in mock_dataread(filename):
    #     print(line)
    #     cols = line.split(",")
    #     time_utc = cols[0]
    #     lat = float(cols[2])
    #     lon = float(cols[3])
    #     alt = float(cols[4])
    #     ch4 = float(cols[9])
    #     c2h6 = float(cols[12])

    
    #     data_dict = {
    #         "Time_UTC": cols[0],
    #         "Time_EPOCH": cols[1],
    #         "Latitude": cols[2],
    #         "Longitude": cols[3],
    #         "Altitude": cols[4],
    #         "WindU": cols[5],
    #         "WindV": cols[6],
    #         "Temperature_C": cols[7],
    #         "RH_percent": cols[8],
    #         "CH4_ppm": cols[9],
    #         "CO2_ppm": cols[10],
    #         "H2O_percent": cols[11],
    #         "C2H6_ppb": cols[12],
    #         "Heading_deg": cols[13],
    #         "GrdSpeed_mps": cols[14],
    #         "AGL_m": cols[15],
    #         "BLIndex_m": cols[16]
    #     }

    #     add_point_5step(lat, lon, time_utc, ch4, c2h6, alt, data_dict, kmlfile)
