# timestamp_cleanup

Repository to clean-up file timestamps by using EXIF or file name.

## Usage:

```
usage: repair_times.py [-h] [--method METHOD] [--path PATH] [-d] [-t TIME_DIFFERENCE] [--debug]
                       [-e EXTENSION] [--list-extensions]

Timestamp repair tool

options:
  -h, --help            show this help message and exit
  --method METHOD       Method how to extract (filename, exif). Default: try Exif otherwise fall-back to
                        filename)
  --path PATH           Path to scan (default PWD)
  -d, --dry-run         Dry-run only
  -t TIME_DIFFERENCE, --time-difference TIME_DIFFERENCE
                        Minimum time difference
  --debug               Debug mode
  -e EXTENSION, --extension EXTENSION
                        Extension to filter (default: all supported video and image extensions
  --list-extensions     List default extensions
  ```
  
  ## Installation
  Install requirments via pip:
  
  ```
  > pip install -r requirements.txt
  > python repair_times.py
  ```
  
  
