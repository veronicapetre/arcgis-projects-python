# https://www.arcgis.com/sharing/rest/content/items/80708a2f5f56426f94c8be97c182176b/data
#download an item by ID

from arcgis.gis import GIS
from datetime import datetime
import zipfile
import os

item_id = "80708a2f5f56426f94c8be97c182176b"
output_path = "./downloads"

# Connect to ArcGIS Online
gis = GIS("https://www.arcgis.com")

# Get the item to download
item = gis.content.get(item_id)

# # Download the item
item.download(save_path=output_path)
# Print information about the item
onlineModified = datetime.fromtimestamp(item.modified/1000.0).strftime('%Y-%m-%d %H:%M:%S')
print("Title:", item.title)
print("Owner:", item.owner)
print("Type:", item.type)
print("Created:", datetime.fromtimestamp(item.created/1000.0).strftime('%Y-%m-%d %H:%M:%S'))
print("Modified:", datetime.fromtimestamp(item.modified/1000.0).strftime('%Y-%m-%d %H:%M:%S'))

# Path to the WinRAR archive file
zip_path = "./downloads/yourfile.zip"

# Path to the output folder where the extracted files will be saved
output_folder = "./downloads"

# Open the WinRAR archive
with zipfile.ZipFile(zip_path, "r") as zip_file:

    # Extract all files from the archive to the output folder
    zip_file.extractall(output_folder)