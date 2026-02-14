# Icon url https://kml4earth.appspot.com/icons.html

import pandas as pd
import numpy as np
import time
import os
import shutil
from datetime import datetime
import configparser

def read_config(filename='PicarroGPSconfig.cfg'):
#def read_config(filename = ):
    """Reads config file and returns config dictionary.

    Parameters
    ----------
    filename : :class:`str <python:str>`
        relative or absolute path to file and filename of the config file.

    Returns
    -------
    :class:`dict <python:dict>`
        Dictionary containing the config values.

    Notes
    -----
    Conversion of the different fields should take place in this routine


    """

    config = configparser.ConfigParser(allow_no_value=True)
    file = os.path.abspath(filename)
    config.read(file)
    print("CONFIG FILE:", file)
    print("EXISTS:", os.path.exists(file))

    config.read(file)
    print("FILES READ:", config.read(file))   
    print("SECTIONS FOUND:", config.sections())    
        #files_read = config.read(file)
        #print("Config file read:", files_read)
        #print("Sections found:", config.sections())

    return config


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


# == KML definition ==========
# colors = ["ff0000ff", "ff00ffff", "ff00ff00", "ff00ff00", "ff0000ff"]
def generate_color_scale(nbins):
    colors = []

    for i in range(nbins):
        ratio = i / (nbins - 1)

        r = int(255 * ratio)
        g = 0
        b = int(255 * (1 - ratio))

        # KML format: AABBGGRR
        color = f"ff{b:02x}{g:02x}{r:02x}"
        colors.append(color)

    return colors

def generate_styles(nbins):
    colors = generate_color_scale(nbins)

    styles = ""
    for i, color in enumerate(colors):
        styles += f"""
<Style id="bin_{i}">
  <IconStyle>
    <color>{color}</color>
    <scale>0.6</scale>
    <Icon>
      <href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>
    </Icon>
  </IconStyle>
</Style>
"""
    return styles

def init_kml(filename, nbins):
    tmp = filename + ".tmp"
    styles = generate_styles(nbins= nbins)
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

def value_to_bin(value, vmin, vmax, nbins):
    if value <= vmin:
        return 0
    if value >= vmax:
        return nbins - 1

    step = (vmax - vmin) / nbins
    return int((value - vmin) / step)

def add_point(lat, lon, name, value, alt, data_dict, filename="merge2.kml"):
    """
    data_dict: {column_name: value, ...}
    """
    
    style_id = value_to_bin(value, vmin, vmax, nbins)   # how to deal with seveeral spieces ???? 
    
    # table_rows = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in data_dict.items()])
    # html_table = f"<table border='1'>{table_rows}</table>"

    tmp = filename + ".tmp"

    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    placemark = f"""
<Placemark>
  <name>{name}</name>
  <styleUrl>#{style_id}</styleUrl>
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
def write_KML(config_filename):
    config = read_config(config_filename)
    reprocessfolder = config['Paths']['reprocessfolder']  # Local buffer
    kml_savefolder = config['Paths']['kmlpath']
    points_per_file = 300
    file_index = 0
    point_counter = 0
    all_files = []

    # Initialize first file
    file_index += 1
    kmlfile = f"{kml_savefolder}/merge3d_{file_index}.kml"
    all_files.append(kmlfile)
    init_kml(kmlfile, config['Device']['nbins'].init())

    write_current_pointer(all_files, active_index=0)

    processed_files = set()

    while True:

        # Sync raw data
        sync_buffer_to_local()
        files = sorted(os.listdir(reprocessfolder)) # files are the current entire
        new_files = files[(file_index-1) * 300 :] # the lastest 300


        # Read new files
        for fname in new_files:

            if fname in processed_files:
                continue

            processed_files.add(fname)

            with open(os.path.join(reprocessfolder, fname), "r") as f:
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
