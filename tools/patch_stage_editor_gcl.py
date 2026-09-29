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

TARGET    = "s21a"
DOOR_ID   = "door_mess"
TRAP_A    = "tr_mess_a"
TRAP_X    = "tr_mess_x"
PROC_NAME = "proc_mess_load"
MODEL_STR = "nst_dor"
SPAWN_X   = 10500
SPAWN_Y   = 0
SPAWN_Z   = 0
SPAWN_DIR = 0   # facing into mess hall; adjust if needed

# Proc: sets spawn position and loads s21a (trap/ntrap pattern, no -f callback)
PROC_BLOCK = f"""
proc {PROC_NAME} {{
    eval($f:000001 = false)
    eval($w:snake_pos_x = {SPAWN_X})
    eval($w:snake_pos_y = {SPAWN_Y})
    eval($w:snake_pos_z = {SPAWN_Z})
    eval($w:000002 = {SPAWN_DIR})
    eval($w:000004 = 0)
    load "{TARGET}" \\
        -map   main \\
        -s     1
}}
"""


def make_door_block(x, z):
    run_z = z - 1500   # point Snake runs toward before fade+load

    door = (
        f"chara DOOR {DOOR_ID} \\\n"
        f"    -p {x},0,{z} \\\n"
        f"    -d 0,0,0 \\\n"
        f"    -m {MODEL_STR} \\\n"
        f"    -t 2 \\\n"
        f"    -w 2000 \\\n"
        f"    -s 70 \\\n"
        f"    -u 0 \\\n"
        f"    -h 400 \\\n"
        f"    -v 4000 \\\n"
        f"    -e 93 90\n"
    )
    trap_a = (
        f"trap {TRAP_A} SNAKE anything? {{\n"
        f"    if (stack:3 == enter) {{\n"
        f"        mesg {DOOR_ID} enter SNAKE 0 0\n"
        f"    }} else {{\n"
        f"        mesg {DOOR_ID} leave stack:2 stack:6 30\n"
        f"    }}\n"
        f"}}\n"
    )
    trap_x = (
        f"ntrap {TRAP_X} SNAKE \\\n"
        f"    -mask  enter \\\n"
        f"    -c     \\\n"
        f"    -exec  {{\n"
        f"        if (stack:7 == 2) {{\n"
        f"            mesg nikita kill\n"
        f"        }} else {{\n"
        f"            pad \\\n"
        f"                -resume\n"
        f"            sound \\\n"
        f"                -x     snd:01ffff0b\n"
        f"            mesg SNAKE  run_move  {x},0,{run_z}  1000,16,-1\n"
        f"            chara FADE_IN_OUT 0x1f8b \\\n"
        f"                -m     0 \\\n"
        f"                -speed 30\n"
        f"            delay \\\n"
        f"                -time  32 \\\n"
        f"                -exec  {{\n"
        f"                    call({PROC_NAME})\n"
        f"                }}\n"
        f"        }}\n"
        f"    }}\n"
    )
    return "\n" + door + "\n" + trap_a + "\n" + trap_x


# Find the last proc block (insert our proc before proc sub_0000)
PROC_0000_RE = re.compile(r'^proc sub_0000\b', re.MULTILINE)

# Find the end of the last trap/ntrap block to insert door block after
LAST_NTRAP_RE = re.compile(
    r'(^ntrap\b[^\n]*\\\n(?:.*\\\n)*.*?\n\s*\}\s*\n)',
    re.MULTILINE
)
# Fallback: find last trap block
LAST_TRAP_RE = re.compile(
    r'(^trap\b[^\n]*\{[^\}]*\}\s*\n)',
    re.MULTILINE | re.DOTALL
)


def patch_gcl(text: str, x: int, z: int) -> str:
    door_block = make_door_block(x, z)

    # 1. Insert proc block before proc sub_0000
    m = PROC_0000_RE.search(text)
    if not m:
        raise ValueError(
            "Could not find 'proc sub_0000' in the GCL.\n"
            "Make sure you exported via ExpGCL (or ViewGCL save) for s08a."
        )
    text = text[:m.start()] + PROC_BLOCK + "\n" + text[m.start():]

    # 2. Append door + trap blocks at the end of the file
    text = text.rstrip('\n') + "\n\n# === Mess Hall door (s21a) ===\n" + door_block + "\n"

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
    print(f"Door  : {DOOR_ID}  X={args.x}  Z={args.z}")
    print(f"Loads : '{TARGET}' with Snake spawning at ({SPAWN_X},{SPAWN_Y},{SPAWN_Z})")

    if args.dry:
        print("\n[DRY RUN] Proc block:")
        print(PROC_BLOCK)
        print("[DRY RUN] Door + trap block:")
        print(make_door_block(args.x, args.z))
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
