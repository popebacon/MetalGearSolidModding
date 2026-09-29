"""
patch_stage_editor_gcl.py
Patches the Stage Editor's exported GCL (from ExpGCL/ViewGCL) to add a
Mess Hall door for s08a that loads stage s21a.

Workflow:
  1. In Stage Editor, load STAGE.mgz → select s08a
  2. Click ExpGCL (or use ViewGCL and save text) → save as e.g. s08a_se.gcl
  3. Run:  python tools/patch_stage_editor_gcl.py s08a_se.gcl s08a_se_patched.gcl
  4. Load s08a_se_patched.gcl in Stage Editor (Load button / Open GCL)
  5. Click Save .gcx → saves the patched binary scenerio.gcx
  6. Run inject to put it back in STAGE.mgz:
       python tools/inject_gcx.py <patched_scenerio.gcx> <STAGE.mgz>

Usage:
    python patch_stage_editor_gcl.py <input.gcl> [output.gcl] [--x X] [--z Z] [--dry]
"""

import sys, os, re, argparse

TARGET     = "s21a"
DOOR_STRID = "s:50f3"
MODEL_STR  = "s:6c6c"
TEX_STRID  = "s:3528"
PROC_NAME  = "sub_9A21"
SPAWN_X    = 10500
SPAWN_Y    = 0
SPAWN_Z    = 0
SPAWN_DIR  = 3072   # facing west into mess hall

# New proc in Stage Editor GCL syntax
PROC_BLOCK = f"""
proc {PROC_NAME} {{
    if (arg1 == s:0dd2) {{
        call(sub_8CD4)
        eval($f:000001 = 0)
        eval($w:800010 = {SPAWN_X})
        eval($w:800012 = {SPAWN_Y})
        eval($w:800014 = {SPAWN_Z})
        eval($w:000002 = {SPAWN_DIR})
        eval($w:000004 = 0)
        load "{TARGET}" \\
            -m s:7df9 \\
            -s 1
    }}
}}
"""

# Door + texture in Stage Editor GCL syntax
def make_door_lines(x, z):
    tx = x - 250
    tz = z + 1750
    door = (
        f"    chara DOOR {DOOR_STRID} \\\n"
        f"        -p {x} 0 {z} \\\n"
        f"        -d 0 3072 0 \\\n"
        f"        -m {MODEL_STR} \\\n"
        f"        -t 1 \\\n"
        f"        -w 1500 \\\n"
        f"        -f {PROC_NAME} \\\n"
        f"        -e 91 88\n"
    )
    tex = (
        f"    chara TEXTURE {TEX_STRID} {tx} 1800 {tz} 0 3072 0 500 400 500 \\\n"
        f"        -I dr_lamp_off \\\n"
        f"        -S  \\\n"
        f"        -a s:dd19 0 5 s:dd19 dr_lamp_off 5 room 3 \\\n"
        f"        -b s:dd19 0 5 s:dd19 dr_lamp_on 5 room 3\n"
    )
    return door + tex

# Insert proc before "proc sub_0000"
PROC_0000_RE = re.compile(r'^proc sub_0000\b', re.MULTILINE)

# Insert door+texture after the last door-style TEXTURE block
# (lines ending with "dr_lamp_on 5 room 3")
LAST_LAMP_TEX_RE = re.compile(
    r'(^    chara TEXTURE \S+ .*?\\\n'
    r'(?:        .*?\\\n)*'
    r'        -b s:dd19 0 5 s:dd19 dr_lamp_on 5 room 3\n)',
    re.MULTILINE
)


def patch_gcl(text: str, x: int, z: int) -> str:
    door_tex = make_door_lines(x, z)

    # 1. Insert proc block before proc sub_0000
    m = PROC_0000_RE.search(text)
    if not m:
        raise ValueError(
            "Could not find 'proc sub_0000' in the GCL.\n"
            "Make sure you exported via ExpGCL (or ViewGCL save) for s08a."
        )
    text = text[:m.start()] + PROC_BLOCK + "\n" + text[m.start():]

    # 2. Insert door+texture after the last door-lamp TEXTURE block
    matches = list(LAST_LAMP_TEX_RE.finditer(text))
    if not matches:
        raise ValueError(
            "Could not find any 'chara TEXTURE ... dr_lamp_on 5 room 3' blocks.\n"
            "Unexpected GCL structure."
        )
    last = matches[-1]
    ins = last.end()
    text = text[:ins] + door_tex + text[ins:]

    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip())
    ap.add_argument("input",  help="Stage Editor GCL file (from ExpGCL)")
    ap.add_argument("output", nargs="?", help="Output path (default: input_patched.gcl)")
    ap.add_argument("--x",   type=int, default=8500)
    ap.add_argument("--z",   type=int, default=5000)
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    in_path = os.path.abspath(args.input)
    if not os.path.isfile(in_path):
        print(f"ERROR: {in_path} not found.")
        sys.exit(1)

    with open(in_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    print(f"Input : {in_path}  ({len(text):,} chars)")
    print(f"Door  : {DOOR_STRID}  X={args.x}  Z={args.z}")
    print(f"Loads : '{TARGET}' with Snake spawning at ({SPAWN_X},{SPAWN_Y},{SPAWN_Z})")

    if args.dry:
        print("\n[DRY RUN] Proc block:")
        print(PROC_BLOCK)
        print("[DRY RUN] Door + texture lines:")
        print(make_door_lines(args.x, args.z))
        return

    patched = patch_gcl(text, args.x, args.z)

    out_path = args.output
    if not out_path:
        base, ext = os.path.splitext(in_path)
        out_path = base + "_patched" + (ext or ".gcl")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(patched)

    print(f"\nWritten: {out_path}  ({len(patched):,} chars)")
    print("Next steps:")
    print("  1. In Stage Editor: Load → open the patched .gcl")
    print("  2. Verify door appears at the right position in the 3D view")
    print("  3. Click 'Save .gcx' to compile the binary GCX")
    print("  4. Run inject_gcx.py to put it back in STAGE.mgz")


if __name__ == "__main__":
    main()
