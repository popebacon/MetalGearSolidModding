# Metal Gear Solid Modding (GOG PC)

Custom stage mods for Metal Gear Solid (PC, GOG version).

## Stages

| Stage | Description | Status |
|-------|-------------|--------|
| [mess_hall](stages/mess_hall/) | Mess hall / dining area referenced by Otacon | In Progress |

## Tools Required

- **mgs1-stagecomp** — compiles annotated `.DAT` source files to binary
- **VR-Disc Patcher** — injects stage DATs into `STAGE.DAT` archive
- **Tim2View** — converts texture spec to TIM2 binary format
- **MGS1 Script Editor** — compiles `.SCR` script sources

## Repository Layout

```
stages/
  <stage_name>/
    stage/      — geometry, header, enemy, item DATs
    textures/   — TIM texture specs
    scripts/    — codec and event scripts
    docs/       — layout diagrams and install notes
```
