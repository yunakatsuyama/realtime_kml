# Icon url https://kml4earth.appspot.com/icons.html

import pandas as pd
import numpy as np
import time
import os
import shutil
from datetime import datetime
import configparser

def read_config(filename):
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
      <href>https://maps.google.com/mapfiles/kml/shapes/road_shield3.png</href>
    </Icon>
  </IconStyle>
  <LabelStyle>
    <scale>0</scale>
</LabelStyle>
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

def add_point(lat, lon, name, value, alt, data_dict , vmin, vmax, nbins, filename="merge2.kml"):
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
  <styleUrl>#bin_{style_id}</styleUrl>
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

def write_current_pointer(all_files, active_index, output_file):
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
    tmp = output_file + ".tmp"

    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)

    os.replace(tmp, output_file)



# == Main ===========
def write_KML(config_filename):

    config = read_config(config_filename)

    # -------------------------
    # Paths
    # -------------------------
    reprocessfolder = config['Paths']['reprocessfolder']
    kml_savefolder = config['Paths']['kmlpath']
    os.makedirs(kml_savefolder, exist_ok=True)

    # -------------------------
    # Device settings
    # -------------------------
    species = config['Device']['species'].split()
    min_values = [float(v) for v in config['Device']['min'].split()]
    max_values = [float(v) for v in config['Device']['max'].split()]
    nbins = config.getint('Device', 'nbins')

    if not (len(species) == len(min_values) == len(max_values)):
        raise ValueError("Mismatch in species/min/max lengths")

    print("Species:", species)

    # -------------------------
    # Initialize per-species state
    # -------------------------
    points_per_file = 300
    file_index = 1
    file_index_slice = 1 
    point_counter_slice = 0

    state = {}

    for i, specie in enumerate(species):

        
        kmlfile = f"{kml_savefolder}/{specie}_{file_index}.kml"

        init_kml(kmlfile, nbins)

        state[specie] = {
            "file_index": file_index,
            "point_counter": 0,
            "kmlfile": kmlfile,
            "all_files": [kmlfile],
            "vmin": min_values[i],
            "vmax": max_values[i]
        }
        pointer_file = f"{kml_savefolder}/current_{specie}.kml"

        write_current_pointer(
            state[specie]["all_files"],
            0,
            pointer_file)
        

    

    processed_files = set()

    # =============================
    # ONE single realtime loop
    # =============================
    while True:

        sync_buffer_to_local()

        files = sorted(os.listdir(reprocessfolder))
        files = files[int((file_index_slice-1) * points_per_file) :]

        for fname in files:

            if fname in processed_files:
                continue

            processed_files.add(fname)

            with open(os.path.join(reprocessfolder, fname), "r") as f:
                lines = f.readlines()

            if len(lines) < 2:
                continue

            cols = lines[1].strip().split(",")

            lat = float(cols[2])
            lon = float(cols[3])
            alt = float(cols[4])

            # Map species to column index
            values = {
                "ch4": float(cols[9]),
                "c2h6": float(cols[12])
            }

            # -------------------------
            # Update ALL species
            # -------------------------
            for specie in species:

                value = values[specie]
                s = state[specie]

                add_point(
                    lat,
                    lon,
                    cols[0],
                    value,
                    alt,
                    {},
                    s["vmin"],
                    s["vmax"],
                    nbins,
                    s["kmlfile"]
                )

                s["point_counter"] += 1

                # Rotate file
                if s["point_counter"] >= points_per_file:

                    s["point_counter"] = 0
                    s["file_index"] += 1

                    newfile = f"{kml_savefolder}/{specie}_{s['file_index']}.kml"

                    init_kml(newfile, nbins)

                    s["kmlfile"] = newfile
                    s["all_files"].append(newfile)

                    write_current_pointer(
                    s["all_files"],
                    active_index=s["file_index"] - 1,
                    output_file=f"{kml_savefolder}/current_{specie}.kml"
                )
            point_counter_slice += 1        
            if point_counter_slice >= points_per_file:
                # Move to next file
                point_counter_slice = 0
                file_index_slice += 1

            print(f"point_counter file_index {point_counter_slice , file_index_slice}")
            
        time.sleep(1)
