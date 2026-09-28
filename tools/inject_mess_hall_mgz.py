"""
inject_mess_hall_mgz.py
Adds the Mess Hall stage (s21a) into an existing STAGE.mgz (PC/GOG version).

Usage:
    python inject_mess_hall_mgz.py <path_to_STAGE.mgz> <path_to_s21a_folder>

Example:
    python inject_mess_hall_mgz.py "G:\\...\\STAGE.mgz" "C:\\...\\stages\\s21a"

A backup of the original is saved as STAGE.mgz.bak before any changes are made.
"""

import zipfile
import shutil
import sys
import os

STAGE_NAME = "s21a"

# Files to inject and where to find them relative to the s21a folder
INJECT_FILES = [
    ("stage/STCMV_MESS.DAT", f"stage/{STAGE_NAME}/STCMV_MESS.DAT"),
    ("stage/STCMV_MESS.HDR", f"stage/{STAGE_NAME}/STCMV_MESS.HDR"),
    ("stage/ENEMY_MESS.DAT", f"stage/{STAGE_NAME}/ENEMY_MESS.DAT"),
    ("stage/ITEM_MESS.DAT",  f"stage/{STAGE_NAME}/ITEM_MESS.DAT"),
    ("scripts/mess_codec.SCR",  f"stage/{STAGE_NAME}/mess_codec.SCR"),
    ("scripts/mess_events.SCR", f"stage/{STAGE_NAME}/mess_events.SCR"),
    ("textures/mess_walls.TIM.txt", f"stage/{STAGE_NAME}/mess_walls.TIM.txt"),
    ("textures/mess_props.TIM.txt", f"stage/{STAGE_NAME}/mess_props.TIM.txt"),
]


def list_stages(mgz_path):
    """Print all stage subdirectories found in the MGZ."""
    with zipfile.ZipFile(mgz_path, "r") as z:
        stages = set()
        for name in z.namelist():
            parts = name.replace("\\", "/").split("/")
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                # Accept both stage/<name>/<file> and <name>/<file>
                if parts[0] == "stage" and len(parts) >= 3:
                    stages.add(parts[1])
                elif parts[0] != "stage":
                    stages.add(parts[0])
        print(f"Stages found in {os.path.basename(mgz_path)}:")
        for s in sorted(stages):
            print(f"  {s}")
    return stages


def inject(mgz_path, stage_dir, dry_run=False):
    # Resolve paths
    mgz_path = os.path.abspath(mgz_path)
    stage_dir = os.path.abspath(stage_dir)
    backup_path = mgz_path + ".bak"
    out_path = mgz_path + ".new"

    if not os.path.isfile(mgz_path):
        print(f"ERROR: {mgz_path} not found.")
        sys.exit(1)
    if not os.path.isdir(stage_dir):
        print(f"ERROR: stage folder not found: {stage_dir}")
        sys.exit(1)

    # Verify source files exist
    missing = []
    for (local_rel, _) in INJECT_FILES:
        full = os.path.join(stage_dir, local_rel)
        if not os.path.isfile(full):
            missing.append(full)
    if missing:
        print("ERROR: Missing source files:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)

    print(f"\nSource : {mgz_path}")
    print(f"Backup : {backup_path}")
    print(f"Output : {mgz_path}  (replaces original after backup)\n")

    if dry_run:
        print("[DRY RUN] No files will be written.\n")

    # Show what's already in the archive
    existing_stages = list_stages(mgz_path)
    if STAGE_NAME in existing_stages:
        print(f"NOTE: '{STAGE_NAME}' already exists in the archive — its files will be replaced.\n")

    print("Files to inject:")
    for (local_rel, zip_path) in INJECT_FILES:
        full = os.path.join(stage_dir, local_rel)
        size = os.path.getsize(full)
        print(f"  {zip_path}  ({size:,} bytes)")

    if dry_run:
        print("\nDry run complete.")
        return

    print()
    confirm = input("Proceed? (Y/N): ").strip().upper()
    if confirm != "Y":
        print("Cancelled.")
        sys.exit(0)

    # Back up the original
    shutil.copy2(mgz_path, backup_path)
    print(f"\nBackup saved: {backup_path}")

    # Copy existing entries (skipping any old s21a entries) into new zip
    skip_prefix = f"stage/{STAGE_NAME}/"
    skip_prefix2 = f"{STAGE_NAME}/"

    with zipfile.ZipFile(mgz_path, "r") as zin, \
         zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:

        kept = 0
        skipped = 0
        for item in zin.infolist():
            norm = item.filename.replace("\\", "/")
            if norm.startswith(skip_prefix) or norm.startswith(skip_prefix2):
                skipped += 1
                continue
            zout.writestr(item, zin.read(item.filename))
            kept += 1

        added = 0
        for (local_rel, zip_path) in INJECT_FILES:
            full = os.path.join(stage_dir, local_rel)
            zout.write(full, zip_path)
            print(f"  [OK] {zip_path}")
            added += 1

    # Replace original with new file
    os.replace(out_path, mgz_path)

    print(f"\nDone.  Kept {kept} existing entries, replaced {skipped} old {STAGE_NAME} entries, added {added} new files.")
    print(f"Output: {mgz_path}")
    print(f"Backup: {backup_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nOptions:")
        print("  --list   Just list stages in the MGZ without modifying it")
        print("  --dry    Dry run: show what would be injected without writing")
        sys.exit(0)

    if sys.argv[1] == "--list":
        if len(sys.argv) < 3:
            print("Usage: inject_mess_hall_mgz.py --list <STAGE.mgz>")
            sys.exit(1)
        list_stages(sys.argv[2])
        sys.exit(0)

    mgz = sys.argv[1]
    stage_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "stages", "s21a"
    )
    dry = "--dry" in sys.argv

    inject(mgz, stage_dir, dry_run=dry)
