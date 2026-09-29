"""
patch_s08a_mess_hall.py
Adds a Mess Hall door to s08a (NWSB B2) that loads stage s21a.

Usage:
    python patch_s08a_mess_hall.py <STAGE.mgz> [--x X] [--z Z] [--dry]

Defaults:  X = 8500   (east wall, same column as stairwell door)
           Z = 5000   (between stairwell door at Z=10500 and corridor mid)

What gets added to scenerio.gcx:
  1. proc 0x9a21  — sets Snake spawn position and calls load "s21a"
  2. chara DOOR   strid:0x50f3  placed at (X, 0, Z), -f proc:0x9a21
  3. chara TEXTURE strid:0x3528  door indicator light, offset from door

A .bak of the original STAGE.mgz is saved before writing.
"""

import zipfile, shutil, sys, os, re

STAGE_NAME  = "s08a"
TARGET      = "s21a"
DOOR_STRID  = "0x50f3"
MODEL_STRID = "0x6c6c"
TEX_STRID   = "0x3528"
PROC_STRID  = "0x9a21"
# Spawn position Snake appears at inside s21a (near the west-side door)
SPAWN_X     = 10500
SPAWN_Y     = 0
SPAWN_Z     = 0
SPAWN_DIR   = 3072   # facing west (into mess hall, away from door)

# ── New proc: sets spawn coords and loads s21a ──────────────────────────────
PROC_BLOCK = f"""
proc {PROC_STRID} /* Mess Hall (s21a) loader */ {{
  {{
    if /*L=29*/ [ arg1 strid:0x0dd2 == END ] {{
      call proc:0x8cd4
      eval /*L=13*/ [ $4:0x000001 0 = END ]
      eval /*L=14*/ [ $1:0x800010 {SPAWN_X} = END ]
      eval /*L=13*/ [ $1:0x800012 {SPAWN_Y} = END ]
      eval /*L=13*/ [ $1:0x800014 {SPAWN_Z} = END ]
      eval /*L=13*/ [ $1:0x000002 {SPAWN_DIR} = END ]
      eval /*L=13*/ [ $1:0x000004 0 = END ]
      load /*L=8*/ "{TARGET}" -m strid:0x7df9 -s 1
      end
    }}
    end
  }}
}}
"""

# ── Door + texture chara lines (formatted at runtime with coords) ────────────
DOOR_LINE_TPL = (
    '    chara /*L=7*/ DOOR:0xb997 strid:{dstrid} '
    '-p {x} 0 {z} -d 0 3072 0 -m strid:{mstrid} -t 1 -w 1500 '
    '-f proc:{proc} -e 91 88\n'
)
# Texture indicator light: offset 250 west, 1800 up, Z+1750
TEX_LINE_TPL = (
    '    chara /*L=34*/ TEXTURE:0x1ad3 strid:{tstrid} '
    '{tx} 1800 {tz} 0 3072 0 500 400 500 '
    '-I strid:0x0e6f -S '
    '-a strid:0xdd19 0 5 strid:0xdd19 strid:0x0e6f 5 strid:0xca87 3 '
    '-b strid:0xdd19 0 5 strid:0xdd19 strid:0x4878 5 strid:0xca87 3\n'
)

LAST_DOOR_RE  = re.compile(r'^    chara\b.*DOOR:0xb997', re.MULTILINE)
SCRIPT_RE     = re.compile(r'^script\b', re.MULTILINE)


def find_gcx(z: zipfile.ZipFile) -> str | None:
    for name in z.namelist():
        norm = name.replace("\\", "/")
        parts = [p for p in norm.split("/") if p]
        if norm.endswith("scenerio.gcx"):
            folder = parts[-2] if len(parts) >= 2 else ""
            if folder == STAGE_NAME:
                return name
    return None


def patch_gcx(text: str, x: int, z: int) -> str:
    door_line = DOOR_LINE_TPL.format(
        dstrid=DOOR_STRID, x=x, z=z, mstrid=MODEL_STRID, proc=PROC_STRID)
    tex_line  = TEX_LINE_TPL.format(
        tstrid=TEX_STRID, tx=x-250, tz=z+1750)

    # 1. Insert proc block just before "script {"
    script_m = SCRIPT_RE.search(text)
    if not script_m:
        raise ValueError("Could not find 'script {' block in GCX.")
    ins_proc = script_m.start()
    text = text[:ins_proc] + PROC_BLOCK + "\n" + text[ins_proc:]

    # 2. Insert door + texture chara after the last existing DOOR chara line
    door_matches = list(LAST_DOOR_RE.finditer(text))
    if not door_matches:
        raise ValueError("No existing 'chara … DOOR:0xb997' lines found.")
    last = door_matches[-1]
    eol  = text.find('\n', last.start())
    if eol == -1:
        eol = len(text)
    ins_door = eol + 1
    text = text[:ins_door] + door_line + tex_line + text[ins_door:]

    return text


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.strip())
    ap.add_argument("mgz", help="Path to STAGE.mgz (will be patched in place)")
    ap.add_argument("--x",   type=int, default=8500, help="Door X (default 8500)")
    ap.add_argument("--z",   type=int, default=5000, help="Door Z (default 5000)")
    ap.add_argument("--dry",  action="store_true", help="Show changes without writing")
    ap.add_argument("--dump", action="store_true", help="Print first 3000 chars of GCX and exit")
    args = ap.parse_args()

    mgz_path = os.path.abspath(args.mgz)
    if not os.path.isfile(mgz_path):
        print(f"ERROR: {mgz_path} not found.")
        sys.exit(1)

    with zipfile.ZipFile(mgz_path, "r") as zin:
        gcx_path = find_gcx(zin)
        if not gcx_path:
            print("ERROR: s08a scenerio.gcx not found in the MGZ.")
            sys.exit(1)
        gcx_bytes = zin.read(gcx_path)
        gcx_text = gcx_bytes.decode("latin-1")

    print(f"GCX : {gcx_path}  ({len(gcx_text):,} chars)")

    if args.dump:
        # List all files in s08a folder
        with zipfile.ZipFile(mgz_path, "r") as zin:
            s08a_files = [n for n in zin.namelist()
                          if f"/{STAGE_NAME}/" in n.replace("\\", "/") or
                             n.replace("\\", "/").startswith(f"{STAGE_NAME}/")]
        print("--- FILES IN s08a ---")
        for f in sorted(s08a_files):
            print(f" {f}")
        print("--- END ---")
        # show embedded ASCII strings (len >= 4) from the binary
        import re as _re
        strings = _re.findall(rb'[ -~]{4,}', gcx_bytes)
        print(f"\n--- EMBEDDED STRINGS ({len(strings)} found) ---")
        for s in strings[:60]:
            print(" ", s)
        return

    print(f"Door: strid:{DOOR_STRID}  X={args.x}  Z={args.z}")
    print(f"Loads stage '{TARGET}' with Snake spawning at ({SPAWN_X},{SPAWN_Y},{SPAWN_Z})")

    patched = patch_gcx(gcx_text, args.x, args.z)

    if args.dry:
        print("\n[DRY RUN] proc block added:")
        print(PROC_BLOCK)
        door_line = DOOR_LINE_TPL.format(
            dstrid=DOOR_STRID, x=args.x, z=args.z,
            mstrid=MODEL_STRID, proc=PROC_STRID)
        tex_line = TEX_LINE_TPL.format(
            tstrid=TEX_STRID, tx=args.x-250, tz=args.z+1750)
        print("[DRY RUN] chara lines added:")
        print(door_line, end="")
        print(tex_line, end="")
        return

    bak = mgz_path + ".bak"
    if not os.path.exists(bak):
        shutil.copy2(mgz_path, bak)
        print(f"Backup: {bak}")

    out = mgz_path + ".new"
    with zipfile.ZipFile(mgz_path, "r") as zin, \
         zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            norm = item.filename.replace("\\", "/")
            if norm.endswith("scenerio.gcx") and f"/{STAGE_NAME}/" in norm:
                zout.writestr(item, patched.encode("latin-1"))
                print(f"  [PATCHED] {item.filename}")
            else:
                zout.writestr(item, zin.read(item.filename))

    os.replace(out, mgz_path)
    print(f"\nDone. {mgz_path}")
    print(f"To verify: open STAGE.mgz in the Stage Editor, load s08a, check for")
    print(f"  door strid:{DOOR_STRID} at X={args.x} Z={args.z}.")
    print(f"Adjust position with --x / --z if needed, then re-run.")


if __name__ == "__main__":
    main()
