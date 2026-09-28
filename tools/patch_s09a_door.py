"""
patch_s09a_door.py
Adds a door trigger to s09a's scenerio.gcx that loads the Mess Hall (s21a).

Usage:
    python patch_s09a_door.py <s09a.mgz> [--x X] [--z Z] [--dry]

Defaults:  X = 9500   (east wall of B2 grating corridor)
           Y = 0      (floor level)
           Z = 1500   (between the two horizontal pipe runs, near stairwell)

The patch appends two lines to the chara block and ntrap block in scenerio.gcx:

    chara DOOR:0xb997 strid:0x50ec -p <X> 0 <Z> -d 0 0 0 -m strid:0x6c75 -t 3 -w 1500 -e 91 88
    ntrap strid:0x50ec SNAKE:0x21ca -m strid:0x0dd2 -c -e { load "s21a" -m strid:0x7df9 -s 1; end }

A .bak copy of the mgz is saved before any changes.
"""

import zipfile, shutil, sys, os, re

TARGET_STAGE = "s21a"
DOOR_STRID   = "0x50ec"
MODEL_STRID  = "0x6c75"   # next free model strid after 0x6c74

# GCX lines to insert (formatted with actual coords at runtime)
DOOR_LINE_TPL = (
    'chara /*L=7*/ DOOR:0xb997 strid:{dstrid} '
    '-p {x} 0 {z} -d 0 0 0 -m strid:{mstrid} -t 3 -w 1500 -e 91 88\n'
)
NTRAP_LINE_TPL = (
    'ntrap /*L=7*/ strid:{dstrid} SNAKE:0x21ca -m strid:0x0dd2 -c -e {{\n'
    '  gsel strid:{dstrid}\n'
    '  load "{stage}" -m strid:0x7df9 -s 1\n'
    '  end\n'
    '}}\n'
)

# We insert after the last existing "chara …DOOR…" line and after the last "ntrap" block
CHARA_DOOR_RE = re.compile(r'^chara\b.*DOOR:', re.MULTILINE)
NTRAP_BLOCK_RE = re.compile(
    r'^(ntrap\b.*?^\})',
    re.MULTILINE | re.DOTALL
)


def find_gcx_path(z: zipfile.ZipFile) -> str | None:
    names = z.namelist()
    # Prefer exact stage folder match (s09a/scenerio.gcx) over variant (s09ar/…)
    for name in names:
        norm = name.replace("\\", "/")
        parts = [p for p in norm.split("/") if p]
        # match stage/s09a/scenerio.gcx  or  s09a/scenerio.gcx  (not s09ar)
        if norm.endswith("scenerio.gcx"):
            # pick the shortest path (most specific non-variant folder)
            folder = parts[-2] if len(parts) >= 2 else ""
            if not folder.endswith("r"):
                return name
    # fallback: any scenerio.gcx
    for name in names:
        if name.replace("\\", "/").endswith("scenerio.gcx"):
            return name
    return None


def patch_gcx(text: str, x: int, z: int) -> str:
    door_line  = DOOR_LINE_TPL.format(dstrid=DOOR_STRID, x=x, z=z, mstrid=MODEL_STRID)
    ntrap_line = NTRAP_LINE_TPL.format(dstrid=DOOR_STRID, stage=TARGET_STAGE)

    # Find insertion point for chara line: after last chara DOOR line
    chara_matches = list(CHARA_DOOR_RE.finditer(text))
    if not chara_matches:
        raise ValueError("No existing 'chara … DOOR:' lines found — wrong GCX?")
    last_chara = chara_matches[-1]
    # advance to end of that line
    eol = text.find('\n', last_chara.start())
    if eol == -1:
        eol = len(text)
    insert_chara_at = eol + 1

    text = text[:insert_chara_at] + door_line + text[insert_chara_at:]

    # After inserting, re-scan for ntrap blocks (text has shifted)
    ntrap_matches = list(NTRAP_BLOCK_RE.finditer(text))
    if not ntrap_matches:
        raise ValueError("No 'ntrap … { … }' blocks found — wrong GCX?")
    last_ntrap = ntrap_matches[-1]
    insert_ntrap_at = last_ntrap.end()
    # ensure we're after the closing newline
    if insert_ntrap_at < len(text) and text[insert_ntrap_at] == '\n':
        insert_ntrap_at += 1

    text = text[:insert_ntrap_at] + ntrap_line + text[insert_ntrap_at:]
    return text


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.strip())
    ap.add_argument("mgz",  help="Path to s09a.mgz (will be patched in place)")
    ap.add_argument("--x",  type=int, default=9500,  help="Door X coordinate (default 9500)")
    ap.add_argument("--z",  type=int, default=1500,  help="Door Z coordinate (default 1500)")
    ap.add_argument("--dry", action="store_true",    help="Print patched GCX without writing")
    args = ap.parse_args()

    mgz_path = os.path.abspath(args.mgz)
    if not os.path.isfile(mgz_path):
        print(f"ERROR: {mgz_path} not found.")
        sys.exit(1)

    with zipfile.ZipFile(mgz_path, "r") as zin:
        gcx_path = find_gcx_path(zin)
        if not gcx_path:
            print("ERROR: scenerio.gcx not found inside the MGZ.")
            sys.exit(1)
        gcx_text = zin.read(gcx_path).decode("latin-1")

    print(f"GCX: {gcx_path}  ({len(gcx_text):,} chars)")
    print(f"Door position: X={args.x}  Y=0  Z={args.z}")

    patched = patch_gcx(gcx_text, args.x, args.z)

    if args.dry:
        # print only the new lines
        new_lines = [l for l in patched.splitlines() if l.strip().startswith(("chara /*L=7*/ DOOR:0xb997 strid:0x50ec",
                                                                                "ntrap /*L=7*/ strid:0x50ec"))]
        print("\n[DRY RUN] Lines that would be added:")
        for l in new_lines:
            print(" ", l)
        return

    bak = mgz_path + ".bak"
    shutil.copy2(mgz_path, bak)
    print(f"Backup: {bak}")

    out_path = mgz_path + ".new"
    with zipfile.ZipFile(mgz_path, "r") as zin, \
         zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            norm = item.filename.replace("\\", "/")
            if norm.endswith("scenerio.gcx"):
                zout.writestr(item, patched.encode("latin-1"))
                print(f"  [PATCHED] {item.filename}")
            else:
                zout.writestr(item, zin.read(item.filename))

    os.replace(out_path, mgz_path)
    print(f"\nDone. Patched {mgz_path}")
    print(f"Load it in the Stage Editor to verify the door position (green door object near X={args.x}, Z={args.z}).")
    print(f"If it's in the wrong spot, run again with --x and --z to adjust, or edit scenerio.gcx directly.")


if __name__ == "__main__":
    main()
