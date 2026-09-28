"""
extract_stage.py
Extracts a single stage from STAGE.mgz into its own .mgz file.

Usage:
    python extract_stage.py <STAGE.mgz> <stage_name> <output.mgz>

Example:
    python extract_stage.py "G:\...\STAGE.mgz" s09a "G:\MGS Modding\s09a.mgz"
"""

import zipfile
import sys
import os

if len(sys.argv) < 4:
    print(__doc__)
    sys.exit(1)

mgz_path  = sys.argv[1]
stage     = sys.argv[2]
out_path  = sys.argv[3]

with zipfile.ZipFile(mgz_path, "r") as zin, \
     zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
    found = 0
    for item in zin.infolist():
        if stage in item.filename:
            zout.writestr(item, zin.read(item.filename))
            print(f"  {item.filename}")
            found += 1

if found == 0:
    print(f"No files found for stage '{stage}'.")
    sys.exit(1)

print(f"\nExtracted {found} files to: {out_path}")
