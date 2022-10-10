import argparse
from exif import Image
import filetype
import os
import time as t
from datetime import datetime
import re


date_match = re.compile('.*(20\d\d)(\d\d)(\d\d)(.)?(\d\d)(\d\d)(.)?(\d\d)?')

parser = argparse.ArgumentParser(description='Timestamp repair tool')
parser.add_argument('--method', default="default", help=
                    'Method how to extract (filename, exif). Default try Exif otherwise fall-back to filename)')
parser.add_argument('--path', default='./', help='Path to scan (default PWD)')
parser.add_argument('-d', '--dry-run', action='store_true', help='Dry-run only')
parser.add_argument('--debug', action='store_true', help='Dry-run only')

args = parser.parse_args()

def check_exif_get_time(file):
    if filetype.is_image(file):
        try:
            with open(file, 'rb') as image_file:
                my_image = Image(image_file)
        except:
            print( "Error reading exif")
            return 0
        if my_image.has_exif:
            return (my_image.get("datetime"))  
    return None

for root, dirs, files in os.walk(args.path):
    for file in files:
        if file.startswith("."):
            continue
        
        file_timestamp = None
        correction_method = None
        if args.debug:
            print ("Checking File: %s" %file)
        stat = os.stat(os.path.join(root, file))
        #import pdb; pdb.set_trace()
        if args.method == "exif" or args.method == "default":
            exif_dt = check_exif_get_time(os.path.join(root, file))
            if exif_dt:
                #2019:09:11 08:08:42
                exif_ts = t.mktime(datetime.strptime(exif_dt, "%Y:%m:%d %H:%M:%S").timetuple())
                file_timestamp = exif_ts
                correction_method = "exif"
                #print ("File %s: Exif detected: %s" % (file, file_timestamp))
        
        if args.method == "file" or (args.method == "default" and file_timestamp is None):
            m = date_match.match(file)
            if m:
                (year, month, day, _,hour, mins, _, secs) = m.groups()
                if not secs or int(secs) > 59:
                    secs = 0
                try:
                    dt = datetime(int(year), int(month), int(day), int(hour), int(mins), int(secs))
                except Exception as e:
                    print(e.message)
                    continue
                correction_method = "file"
                file_timestamp = t.mktime(dt.timetuple())
        if file_timestamp is not None:
            if abs(file_timestamp - stat.st_mtime) > 3600:
                print ("File: %s - file date: %s <> %s detected" % (file, 
                    datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.fromtimestamp(file_timestamp).strftime('%Y-%m-%d %H:%M:%S')))
                if not args.dry_run:
                    print ("Correcting file: %s with method %s" % (file, correction_method))
                    os.utime(os.path.join(root, file), (file_timestamp, file_timestamp))