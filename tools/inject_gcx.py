"""
inject_gcx.py
Injects a patched scenerio.gcx back into STAGE.mgz for a given stage.

Usage:
    python tools/inject_gcx.py <scenerio.gcx> <STAGE.mgz> [--stage STAGENAME]

Example:
    python tools/inject_gcx.py scenerio.gcx "G:\\Program Files (x86)\\GOG Galaxy\\Games\\Metal Gear Solid - Modded\\STAGE.mgz" --stage s08a

A .bak of the original STAGE.mgz is saved alongside it before writing.
"""

import zipfile, shutil, sys, os, argparse


def find_gcx(z: zipfile.ZipFile, stage: str) -> str | None:
    for name in z.namelist():
        norm = name.replace("\\", "/")
        parts = [p for p in norm.split("/") if p]
        if norm.endswith("scenerio.gcx"):
            folder = parts[-2] if len(parts) >= 2 else ""
            if folder == stage:
                return name
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip())
    ap.add_argument("gcx",   help="Patched scenerio.gcx file")
    ap.add_argument("mgz",   help="Path to STAGE.mgz")
    ap.add_argument("--stage", default="s08a", help="Stage folder name (default: s08a)")
    args = ap.parse_args()

    gcx_path = os.path.abspath(args.gcx)
    mgz_path = os.path.abspath(args.mgz)

    if not os.path.isfile(gcx_path):
        print(f"ERROR: {gcx_path} not found.")
        sys.exit(1)
    if not os.path.isfile(mgz_path):
        print(f"ERROR: {mgz_path} not found.")
        sys.exit(1)

    with open(gcx_path, "rb") as f:
        gcx_data = f.read()
    print(f"GCX  : {gcx_path}  ({len(gcx_data):,} bytes)")

    with zipfile.ZipFile(mgz_path, "r") as zin:
        target = find_gcx(zin, args.stage)
        if not target:
            print(f"ERROR: scenerio.gcx for stage '{args.stage}' not found in {mgz_path}")
            sys.exit(1)
        print(f"Target entry: {target}")

    bak = mgz_path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(mgz_path, bak)
        print(f"Backup: {bak}")

    out = mgz_path + ".new"
    with zipfile.ZipFile(mgz_path, "r") as zin, \
         zipfile.ZipFile(out, "w") as zout:
        for item in zin.infolist():
            data = gcx_data if item.filename == target else zin.read(item.filename)
            # preserve original compression type per entry
            item.compress_type = zin.getinfo(item.filename).compress_type
            zout.writestr(item, data)
            if item.filename == target:
                print(f"  [INJECTED] {item.filename}  ({len(gcx_data):,} bytes)")
    os.replace(out, mgz_path)
    print(f"\nDone. {mgz_path} updated.")
    print(f"Launch the game and enter {args.stage} to test.")


if __name__ == "__main__":
    main()
