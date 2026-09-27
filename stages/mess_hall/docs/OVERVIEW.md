# Mess Hall / Dining Area — Custom Stage

Stage ID: `j75jh3` (STAGE_MESS_HALL)

## Lore Reference

Otacon mentions the mess hall during a Codec call with Snake on Shadow Moses Island.
The soldiers take their meals in a single large dining area off the B2 grating
corridor of the **Nuclear Warhead Storage Building**, accessed through a door on the
east wall of the corridor — between the two large pipe runs, east of the central
stairwell. This stage brings that space to life as a traversable environment.

## Layout Overview

```
  [NORTH WALL — kitchen side]
  +------------------------------------------+
  |  Kitchen / Serving Counter (raised 0.5m) |
  |  [TABLE A]  [TABLE B]  [TABLE C]          |
  |                                           |
  |  [TABLE D]  [TABLE E]  [TABLE F]          |
  |                                           |
  |  [TABLE G]  [TABLE H]  [TABLE I]          |
  |                                           |
  |                              [DOOR >>>]  |  ← east wall, to NWSB B2 corridor
  +------------------------------------------+
  [SOUTH WALL — solid]

Room dimensions: 24m x 16m x 3.5m (W x D x H)
Single entry/exit on east wall (x=12.0, z=-6.75), 2.0m wide × 2.5m tall.
```

## Connection Point

The door sits on the east wall of the mess hall, opening into the **B2 grating
corridor of the Nuclear Warhead Storage Building**, between the two large horizontal
pipe runs visible east of the central stairwell. The X mark on the reference
screenshot pins the door between those pipe runs on the south segment of the
grating floor.

In-game flow: Snake descends to B2 via the stairwell, moves east past the pipes,
and the door is on the left-hand (south) wall of the grating corridor.

## Files

| File | Description |
|------|-------------|
| `stage/STCMV_MESS.DAT` | Stage geometry / collision data |
| `stage/STCMV_MESS.HDR` | Stage header (room ID, spawn points, camera volumes) |
| `stage/ENEMY_MESS.DAT` | Enemy patrol routes and initial placements |
| `stage/ITEM_MESS.DAT`  | Item placements (rations, ammo cans, hidden items) |
| `textures/mess_walls.TIM`  | Wall / floor / ceiling texture sheet (TIM2 format) |
| `textures/mess_props.TIM`  | Prop textures (tables, trays, benches) |
| `scripts/mess_codec.SCR`   | Codec trigger script (Otacon call on entry) |
| `scripts/mess_events.SCR`  | Guard dialogue, alert behaviours, ambient sounds |

## Installation (GOG PC Version)

1. Back up your original `STAGE.DAT` and `STAGE.HDR` in the GOG install folder.
2. Use **VR-Disc Patcher** (or equivalent DAT injector) to inject:
   - `STCMV_MESS.DAT` → slot `0x48` (first free custom slot)
   - `STCMV_MESS.HDR` → matching header slot
3. Copy `mess_walls.TIM` and `mess_props.TIM` into the texture archive.
4. Inject `mess_codec.SCR` and `mess_events.SCR` via the script patcher.
5. Patch the **NWSB B2 corridor stage** (`0x09`) to add a door trigger on its east
   wall at the X mark position (between the two pipe runs, south of stairwell):
   - Add `DOOR_TRIGGER` at the corridor's local coordinates for that wall segment
   - Set target to `STAGE_MESS_HALL` (0x48), `target_spawn = 0x00`

## Camera Volumes

Three fixed overhead cameras cover the room:
- `CAM_MESS_A` — kitchen / north half
- `CAM_MESS_B` — centre tables
- `CAM_MESS_C` — south exit corridor blend
