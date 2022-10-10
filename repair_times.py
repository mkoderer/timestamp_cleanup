# The MIT License (MIT)
# Copyright (c) 2022 Marc Koderer

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import argparse
from exif import Image
import filetype
import os
import time as t
from datetime import datetime
import re
import sys
import pprint

stats = {}

date_match = re.compile('.*(20\d\d)(\d\d)(\d\d)(.)?(\d\d)(\d\d)(.)?(\d\d)?')

parser = argparse.ArgumentParser(description='Timestamp repair tool')
parser.add_argument('--method', default="default", help=
                    'Method how to extract (filename, exif). Default: try Exif otherwise fall-back to filename)')
parser.add_argument('--path', default='./', help='Path to scan (default PWD)')
parser.add_argument('-d', '--dry-run', action='store_true', help='Dry-run only')
parser.add_argument('-t', '--time-difference', default=3600, type=int,  help='Minimum time difference')
parser.add_argument('--debug', action='store_true', help='Debug mode')
parser.add_argument('-e', '--extension',  help='Extension to filter (default: all supported video and image extensions')
parser.add_argument('--list-extensions',  action='store_true', help='List default extensions')

args = parser.parse_args()

# thanks: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '.' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()  # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)


def get_valid_file_extensions():
    if args.extension:
        return [args.extension]
    else:
        ext = []
        for img in filetype.image_matchers:
            ext.append(img.extension)
        for vid in filetype.video_matchers:
            ext.append(vid.extension)
        return ext

def check_exif_get_time(file):
    if filetype.is_image(file):
        try:
            with open(file, 'rb') as image_file:
                my_image = Image(image_file)
        except:
            print( "Error reading exif %s" % file)
            return 0
        if my_image.has_exif:
            return (my_image.get("datetime"))  
    return None

def correct_files(path):
    print ("Checking path: %s" % path)
    for root, dirs, files in os.walk(path):
        stats[root] = {"number_of_total_files": len(files),
                       "number_of_files": 0,
                       "number_of_dir": len(dirs),
                       "found_wrong_ts": 0,
                       "corrected_with_file": 0,
                       "corrected_with_exif": 0,
                       "dry_run": args.dry_run}
        for c, file in enumerate(files):
            progress(c, len(files))
            extension = get_valid_file_extensions()
            if file.startswith("."):
                continue
            if not os.path.splitext(file) in get_valid_file_extensions():
                continue

            file_timestamp = None
            correction_method = None
            stat[root]["number_of_files"] += 1
            if args.debug:
                print ("Checking File: %s" %file)
            stat = os.stat(os.path.join(root, file))
            #import pdb; pdb.set_trace()
            if args.method == "exif" or args.method == "default":
                exif_dt = check_exif_get_time(os.path.join(root, file))
                if exif_dt:
                    #2019:09:11 08:08:42
                    try:
                        exif_ts = t.mktime(datetime.strptime(exif_dt, "%Y:%m:%d %H:%M:%S").timetuple())
                        file_timestamp = exif_ts
                        correction_method = "exif"
                    except:
                        print ("Invalid exif field for file %s" % file)
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
                        print(e)
                        continue
                    correction_method = "file"
                    file_timestamp = t.mktime(dt.timetuple())
            if file_timestamp is not None:
                if abs(file_timestamp - stat.st_mtime) > args.time_difference:
                    stats[path]["found_wrong_ts"] += 1
                    if correction_method == "file":
                        stats[path]["corrected_with_file"] += 1
                    elif correction_method == "exif":
                        stats[path]["corrected_with_exif"] += 1
                    print ("File: %s - file date: %s <> %s detected" % (file, 
                        datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        datetime.fromtimestamp(file_timestamp).strftime('%Y-%m-%d %H:%M:%S')))
                    if not args.dry_run:
                        print ("Correcting file: %s with method %s" % (file, correction_method))
                        os.utime(os.path.join(root, file), (file_timestamp, file_timestamp))

if __name__ == "__main__":
    if args.list_extensions:
        pprint.pprint(get_valid_file_extensions())
    else:
        correct_files(args.path)
        pprint.pprint(stats)