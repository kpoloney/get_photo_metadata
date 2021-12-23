import sys
import csv
import os
import exif
from PIL import Image, ImageFile, IptcImagePlugin
from iptcinfo3 import IPTCInfo, c_datasets_r

file_dir = sys.argv[1]
if not os.path.exists(file_dir):
    print("Invalid directory path")
    quit()
files = os.listdir(file_dir)
im_exts = ['.png', '.jpg', '.jpeg', '.tiff', '.gif', '.jp2', '.jpm', '.jpx', '.bmd', '.pct', '.psd', '.tga']

# Extract EXIF metadata from all images in directory.
# Create list of dictionaries where each list item corresponds to one image.
exif_data = []
for fn in files:
    if os.path.splitext(fn)[1].lower() not in im_exts:
        continue
    else:
        with open(os.path.join(file_dir, fn), 'rb') as im:
            img = exif.Image(im)
            if not img.has_exif:
                continue
            else:
                im_data = {}
                im_data['filename'] = fn
                for tag in img.list_all():
                    try:
                        im_data[tag] = getattr(img, tag)
                    except:
                        # print("Couldn't read tag value: ", tag)
                        continue
                exif_data.append(im_data)

#Export EXIF metadata to csv
if len(exif_data) > 0:
    csv_path = os.path.join(file_dir, "exif_data.csv")
    if os.path.exists(csv_path):
        print("exif_data.csv already exists")
        new = input("Please enter a unique filename (ending in .csv): ")
        csv_path = os.path.join(file_dir, new)
    all_tags = []
    for img in exif_data:
        for k in img.keys():
            all_tags.append(k)
    tag_list = list(set(all_tags))
    with open(csv_path, 'w', newline="") as c:
        writer = csv.DictWriter(c, fieldnames=tag_list)
        writer.writeheader()
        for item in exif_data:
            writer.writerow(item)

# Get IPTC metadata if it has any (only tiffs and jpgs)
iptc_data = []
for fn in files:
    if os.path.splitext(fn)[1].lower() not in ['.tiff', '.jpg', '.jpeg']:
        continue
    else:
        b = Image.open(os.path.join(file_dir, fn))
        if IptcImagePlugin.getiptcinfo(b) is None:
            continue
        else:
            with open(os.path.join(file_dir, fn), 'rb') as f:
                inf = IPTCInfo(f, inp_charset='utf-8', out_charset='utf-8')
            ip_data = {}
            ip_data['filename'] = fn
            for key in c_datasets_r.keys(): # can't iterate through keys of IPTCInfo object directly
                if inf[key] is not None:
                    newval = inf[key]
                    ip_data[key] = newval
            iptc_data.append(ip_data)

# Write IPTC metadata to csv
if len(iptc_data) > 0:
    csv_path = os.path.join(file_dir, "iptc_data.csv")
    if os.path.exists(csv_path):
        print("iptc_data.csv already exists")
        new = input("Please enter a unique filename: ")
        csv_path = os.path.join(sys.argv[1], new)
    iptc_tags = []
    for img in iptc_data:
        for k in img.keys():
            iptc_tags.append(k)
    iptc_tag_list = list(set(iptc_tags))
    with open(csv_path, 'w', newline="") as c:
        writer = csv.DictWriter(c, fieldnames=iptc_tag_list)
        writer.writeheader()
        for item in iptc_data:
            writer.writerow(item)