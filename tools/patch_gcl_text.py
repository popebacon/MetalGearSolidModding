"""
patch_gcl_text.py
Patches the decompiled GCL text for s08a (from Stage Editor's ViewGCX output)
to add a Mess Hall door that loads stage s21a.

Workflow:
  1. In Stage Editor, load STAGE.mgz → select s08a → click ViewGCX
  2. Select All / Copy the full text → save to a file (e.g. s08a.gcl)
  3. Run:  python tools/patch_gcl_text.py s08a.gcl s08a_patched.gcl
  4. Load s08a_patched.gcl back in Stage Editor (if it supports GCL loading),
     or use a GCX compiler to produce a new scenerio.gcx.

Usage:
    python patch_gcl_text.py <input.gcl> [output.gcl] [--x X] [--z Z] [--dry]

Defaults:  X = 8500   (east wall, same column as stairwell door at X=8500,Z=10500)
           Z = 5000   (south of stairwell, toward corridor mid)
"""

import sys, os, re, argparse

TARGET      = "s21a"
DOOR_STRID  = "0x50f3"
MODEL_STRID = "0x6c6c"
TEX_STRID   = "0x3528"
PROC_STRID  = "0x9a21"
SPAWN_X     = 10500
SPAWN_Y     = 0
SPAWN_Z     = 0
SPAWN_DIR   = 3072   # facing west into mess hall

PROC_BLOCK = f"""proc {PROC_STRID} /* Mess Hall (s21a) loader */ {{
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

DOOR_LINE_TPL = (
    '    chara /*L=7*/ DOOR:0xb997 strid:{dstrid} '
    '-p {x} 0 {z} -d 0 3072 0 -m strid:{mstrid} -t 1 -w 1500 '
    '-f proc:{proc} -e 91 88\n'
)
TEX_LINE_TPL = (
    '    chara /*L=34*/ TEXTURE:0x1ad3 strid:{tstrid} '
    '{tx} 1800 {tz} 0 3072 0 500 400 500 '
    '-I strid:0x0e6f -S '
    '-a strid:0xdd19 0 5 strid:0xdd19 strid:0x0e6f 5 strid:0xca87 3 '
    '-b strid:0xdd19 0 5 strid:0xdd19 strid:0x4878 5 strid:0xca87 3\n'
)

# Match the last existing DOOR chara line (indented with spaces)
LAST_DOOR_RE = re.compile(r'^[ \t]*chara\b.*DOOR:0xb997', re.MULTILINE)
# Match "script {" or "script{" at start of line
SCRIPT_RE    = re.compile(r'^script\s*\{', re.MULTILINE)


def patch_gcl(text: str, x: int, z: int) -> str:
    door_line = DOOR_LINE_TPL.format(
        dstrid=DOOR_STRID, x=x, z=z, mstrid=MODEL_STRID, proc=PROC_STRID)
    tex_line  = TEX_LINE_TPL.format(
        tstrid=TEX_STRID, tx=x-250, tz=z+1750)

    # 1. Insert proc block just before "script {"
    script_m = SCRIPT_RE.search(text)
    if not script_m:
        raise ValueError(
            "Could not find 'script {' in the GCL text.\n"
            "Make sure you copied the FULL ViewGCX output (it should end with a "
            "'script { ... }' block containing all the chara/ntrap lines)."
        )
    text = text[:script_m.start()] + PROC_BLOCK + "\n" + text[script_m.start():]

    # 2. Insert door + texture chara after the last existing DOOR chara
    door_matches = list(LAST_DOOR_RE.finditer(text))
    if not door_matches:
        raise ValueError(
            "No existing 'chara … DOOR:0xb997' lines found in the GCL.\n"
            "The ViewGCX output should contain lines like:\n"
            "    chara /*L=7*/ DOOR:0xb997 strid:0x50f2 ..."
        )
    last = door_matches[-1]
    eol  = text.find('\n', last.start())
    if eol == -1:
        eol = len(text)
    text = text[:eol+1] + door_line + tex_line + text[eol+1:]

    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip())
    ap.add_argument("input",  help="Path to the decompiled GCL text file (ViewGCX output)")
    ap.add_argument("output", nargs="?", help="Output path (default: input_patched.gcl)")
    ap.add_argument("--x",   type=int, default=8500, help="Door X coordinate (default 8500)")
    ap.add_argument("--z",   type=int, default=5000, help="Door Z coordinate (default 5000)")
    ap.add_argument("--dry", action="store_true", help="Print what would be added, don't write")
    args = ap.parse_args()

    in_path = os.path.abspath(args.input)
    if not os.path.isfile(in_path):
        print(f"ERROR: {in_path} not found.")
        sys.exit(1)

    with open(in_path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    print(f"Input : {in_path}  ({len(text):,} chars)")
    print(f"Door  : strid:{DOOR_STRID}  X={args.x}  Z={args.z}")
    print(f"Loads : '{TARGET}' with Snake spawning at ({SPAWN_X},{SPAWN_Y},{SPAWN_Z})")

    # Quick sanity check
    if "script" not in text:
        print("\nWARNING: 'script' not found in the input — are you sure this is a ViewGCX output?")
        print("First 200 chars:")
        print(repr(text[:200]))
        sys.exit(1)

    patched = patch_gcl(text, args.x, args.z)

    if args.dry:
        print("\n[DRY RUN] Proc block that would be added:")
        print(PROC_BLOCK)
        door_line = DOOR_LINE_TPL.format(
            dstrid=DOOR_STRID, x=args.x, z=args.z,
            mstrid=MODEL_STRID, proc=PROC_STRID)
        tex_line = TEX_LINE_TPL.format(
            tstrid=TEX_STRID, tx=args.x-250, tz=args.z+1750)
        print("[DRY RUN] Chara lines that would be added:")
        print(door_line, end="")
        print(tex_line, end="")
        return

    out_path = args.output
    if not out_path:
        base, ext = os.path.splitext(in_path)
        out_path = base + "_patched" + (ext or ".gcl")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(patched)

    print(f"\nWritten: {out_path}  ({len(patched):,} chars)")
    print("Next steps:")
    print("  1. Load the patched .gcl in the Stage Editor (if it supports GCL input)")
    print("     OR use a GCX compiler to produce a new scenerio.gcx")
    print("  2. Verify the door appears at the right position")
    print("  3. Adjust --x / --z and re-run if needed")


if __name__ == "__main__":
    main()
