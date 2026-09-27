# Mess Hall / Dining Area — Custom Stage

Stage ID: `j75jh3` (STAGE_MESS_HALL)

## Lore Reference

Otacon mentions the mess hall during a Codec call with Snake on Shadow Moses Island.
The soldiers take their meals in a single large dining area on the underground base's
B2 level, adjacent to the communications towers access corridor. This stage brings
that space to life as a traversable environment.

## Layout Overview

```
  [NORTH WALL]
  +------------------------------------------+
  |  Kitchen / Serving Counter (raised 0.5m) |
  |  [TABLE A]  [TABLE B]  [TABLE C]          |
  |                                           |
  |  [TABLE D]  [TABLE E]  [TABLE F]          |
  |                                           |
  |  [TABLE G]  [TABLE H]  [TABLE I]          |
  |                                           |
  |  EXIT WEST          EXIT EAST             |
  +------------------------------------------+
  [SOUTH WALL]

Room dimensions: 24m x 16m x 3.5m (W x D x H)
```

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
5. Add a room-transition trigger from the desired corridor stage to `STAGE_MESS_HALL`.

## Camera Volumes

Three fixed overhead cameras cover the room:
- `CAM_MESS_A` — kitchen / north half
- `CAM_MESS_B` — centre tables
- `CAM_MESS_C` — south exit corridor blend
